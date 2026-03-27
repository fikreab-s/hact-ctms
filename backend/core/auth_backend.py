"""
Core — Custom Keycloak OIDC Authentication Backend
=====================================================
Extends mozilla-django-oidc to:
1. Auto-create/update Django User on first Keycloak login
2. Map keycloak_id (sub claim) to User.keycloak_id
3. Sync user roles from Keycloak realm_access.roles
4. Support JWT Bearer token authentication for DRF API calls
"""

import logging
import jwt
import requests

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()
logger = logging.getLogger("hact_ctms.auth")


class KeycloakOIDCBackend:
    """Django authentication backend for Keycloak OIDC.

    Called by mozilla-django-oidc or directly for session-based auth.
    Auto-creates a Django User on first login using Keycloak claims.
    """

    def authenticate(self, request, **kwargs):
        """Not used directly — see KeycloakJWTAuthentication for API auth."""
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def create_or_update_user(claims):
        """Create or update a Django User from Keycloak token claims.

        Handles three cases:
        1. User already exists with this keycloak_id → update
        2. User exists with matching username but different keycloak_id → link + update
        3. New user entirely → create

        Args:
            claims: Decoded JWT claims dict containing sub, email,
                    preferred_username, given_name, family_name, etc.

        Returns:
            User instance
        """
        import uuid as uuid_mod

        keycloak_id = claims.get("sub")
        if not keycloak_id:
            raise ValueError("Token missing 'sub' claim")

        # Convert string to UUID
        try:
            kc_uuid = uuid_mod.UUID(keycloak_id)
        except ValueError:
            raise ValueError(f"Invalid 'sub' claim (not a UUID): {keycloak_id}")

        email = claims.get("email", "")
        username = claims.get("preferred_username", email)

        # Case 1: User already linked to this Keycloak ID
        try:
            user = User.objects.get(keycloak_id=kc_uuid)
            user.username = username
            user.email = email or user.email
            user.first_name = claims.get("given_name", "") or user.first_name
            user.last_name = claims.get("family_name", "") or user.last_name
            user.is_active = True
            user.save(update_fields=["username", "email", "first_name", "last_name", "is_active"])
            logger.info(f"Updated user '{username}' from Keycloak (sub={keycloak_id})")
            _sync_keycloak_roles(user, claims)
            return user
        except User.DoesNotExist:
            pass

        # Case 2: User exists with this username but not linked to Keycloak yet
        try:
            user = User.objects.get(username=username)
            user.keycloak_id = kc_uuid
            user.email = email or user.email
            user.first_name = claims.get("given_name", "") or user.first_name
            user.last_name = claims.get("family_name", "") or user.last_name
            user.is_active = True
            user.save(update_fields=["keycloak_id", "email", "first_name", "last_name", "is_active"])
            logger.info(f"Linked existing user '{username}' to Keycloak (sub={keycloak_id})")
            _sync_keycloak_roles(user, claims)
            return user
        except User.DoesNotExist:
            pass

        # Case 3: Completely new user
        user = User.objects.create(
            keycloak_id=kc_uuid,
            username=username,
            email=email,
            first_name=claims.get("given_name", ""),
            last_name=claims.get("family_name", ""),
            is_active=True,
        )
        logger.info(f"Created new user '{username}' from Keycloak (sub={keycloak_id})")

        # Sync Keycloak roles to Django UserRole table
        _sync_keycloak_roles(user, claims)

        return user


def _sync_keycloak_roles(user, claims):
    """Sync Keycloak realm roles → Django Role + UserRole.

    Reads roles from `realm_access.roles` in the JWT token and maps
    them to the accounts.Role table via accounts.UserRole.
    """
    from accounts.models import Role, UserRole

    kc_roles = claims.get("realm_access", {}).get("roles", [])
    # Filter out Keycloak internal roles
    internal_roles = {"offline_access", "uma_authorization", "default-roles-hact"}
    app_roles = [r for r in kc_roles if r not in internal_roles]

    if not app_roles:
        return

    current_role_names = set(
        UserRole.objects.filter(user=user).values_list("role__name", flat=True)
    )

    for role_name in app_roles:
        if role_name not in current_role_names:
            role, _ = Role.objects.get_or_create(
                name=role_name,
                defaults={"description": f"Auto-synced from Keycloak: {role_name}"},
            )
            UserRole.objects.get_or_create(user=user, role=role)
            logger.info(f"Assigned role '{role_name}' to user '{user.username}'")


# =============================================================================
# JWT Bearer Token Authentication for DRF
# =============================================================================

# Cache for Keycloak public keys
_jwks_cache = {"keys": None, "fetched_at": None}


def _get_keycloak_public_keys():
    """Fetch and cache Keycloak's JWKS (public keys) for JWT verification."""
    import time

    # Cache keys for 5 minutes
    if _jwks_cache["keys"] and _jwks_cache["fetched_at"]:
        if time.time() - _jwks_cache["fetched_at"] < 300:
            return _jwks_cache["keys"]

    jwks_url = settings.OIDC_OP_JWKS_ENDPOINT
    try:
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()
        jwks = response.json()
        _jwks_cache["keys"] = jwks
        _jwks_cache["fetched_at"] = time.time()
        logger.debug(f"Fetched JWKS from {jwks_url}")
        return jwks
    except Exception as e:
        logger.error(f"Failed to fetch JWKS from {jwks_url}: {e}")
        # Return cached keys if available, even if stale
        if _jwks_cache["keys"]:
            return _jwks_cache["keys"]
        raise AuthenticationFailed("Unable to verify token: JWKS unavailable")


class KeycloakJWTAuthentication(BaseAuthentication):
    """DRF authentication class that validates Keycloak JWT Bearer tokens.

    Usage in ViewSets: Set in DEFAULT_AUTHENTICATION_CLASSES or per-view.

    Flow:
    1. Extract Bearer token from Authorization header
    2. Fetch Keycloak's JWKS public keys (cached)
    3. Decode and verify the JWT signature
    4. Auto-create/update Django User from token claims
    5. Return (user, decoded_token) for DRF
    """

    keyword = "Bearer"

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith(f"{self.keyword} "):
            return None  # Not a Bearer token — let other authenticators try

        token = auth_header[len(self.keyword) + 1:]
        return self._authenticate_token(token)

    def _authenticate_token(self, token):
        """Decode, verify, and map a Keycloak JWT to a Django User."""
        try:
            # Get the signing key from Keycloak JWKS
            jwks = _get_keycloak_public_keys()
            jwks_client = jwt.PyJWKClient.__new__(jwt.PyJWKClient)
            jwks_client.jwk_set = jwt.PyJWKSet.from_dict(jwks)

            # Get the signing key for this specific token
            header = jwt.get_unverified_header(token)
            key = None
            for jwk_key in jwks_client.jwk_set.keys:
                if jwk_key.key_id == header.get("kid"):
                    key = jwk_key.key
                    break

            if not key:
                raise AuthenticationFailed("Token signing key not found in JWKS")

            # Decode and verify the token
            # Accept tokens issued via both external (localhost) and
            # internal (keycloak:8080) URLs, since Keycloak stamps the
            # issuer based on the URL the client used to reach it.
            decoded = jwt.decode(
                token,
                key,
                algorithms=[settings.OIDC_RP_SIGN_ALGO],
                options={
                    "verify_exp": True,
                    "verify_aud": False,  # Keycloak aud is often "account", not client_id
                    "verify_iss": False,  # We verify manually below
                },
            )

            # Manual audience verification — Keycloak access tokens
            # typically have aud="account" and azp="hact-ctms"
            token_aud = decoded.get("aud", "")
            token_azp = decoded.get("azp", "")
            client_id = settings.OIDC_RP_CLIENT_ID

            # Accept if aud matches OR azp matches
            aud_list = token_aud if isinstance(token_aud, list) else [token_aud]
            if client_id not in aud_list and token_azp != client_id:
                raise AuthenticationFailed(
                    f"Token not issued for client '{client_id}'. "
                    f"aud={token_aud}, azp={token_azp}"
                )

            # Manual issuer verification — accept multiple valid issuers
            token_issuer = decoded.get("iss", "")
            valid_issuers = {
                # External URL (browser / Postman via NGINX)
                settings.OIDC_OP_AUTHORIZATION_ENDPOINT.rsplit("/protocol/", 1)[0],
                # Internal Docker URL
                settings.OIDC_OP_TOKEN_ENDPOINT.rsplit("/protocol/", 1)[0],
                # Explicit issuer setting
                getattr(settings, "OIDC_OP_ISSUER", ""),
            }
            valid_issuers.discard("")

            if token_issuer not in valid_issuers:
                logger.warning(
                    f"Token issuer '{token_issuer}' not in valid issuers: {valid_issuers}"
                )
                raise AuthenticationFailed(
                    f"Token issuer mismatch. Got '{token_issuer}'"
                )

            # Create or update the Django User from Keycloak claims
            user = KeycloakOIDCBackend.create_or_update_user(decoded)
            return (user, decoded)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidAudienceError:
            raise AuthenticationFailed("Token audience mismatch")
        except jwt.DecodeError as e:
            raise AuthenticationFailed(f"Invalid token: {e}")
        except AuthenticationFailed:
            raise  # Re-raise DRF AuthenticationFailed as-is
        except Exception as e:
            import traceback
            logger.error(f"JWT authentication failed: {e}\n{traceback.format_exc()}")
            raise AuthenticationFailed(f"Authentication failed: {e}")

    def authenticate_header(self, request):
        return f'{self.keyword} realm="hact-ctms"'
