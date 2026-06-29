"""
seed_default_users — Create default HACT users on first deployment.

This runs idempotently on every container start (via entrypoint.sh).
It creates Django users so that Keycloak OIDC login can auto-link them.

Usage:
    python manage.py seed_default_users
"""

import logging

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

logger = logging.getLogger("accounts")

# Default users to seed on first deployment
# Keycloak will set the real passwords — these Django passwords
# are only used for e-signature verification (check_password)
DEFAULT_USERS = [
    {
        "username": "hact-user",
        "email": "hact-user@hacts.org",
        "first_name": "HACT",
        "last_name": "User",
        "password": "hact-user",
        "is_staff": True,
        "is_superuser": False,
        "role": "admin",
    },
    {
        "username": "hact-admin",
        "email": "hact-admin@hacts.org",
        "first_name": "HACT",
        "last_name": "Admin",
        "password": "hact-admin",
        "is_staff": True,
        "is_superuser": True,
        "role": "admin",
    },
]


class Command(BaseCommand):
    help = "Seed default HACT users (idempotent — safe to run multiple times)"

    def handle(self, *args, **options):
        User = get_user_model()
        created_count = 0
        updated_count = 0

        for user_data in DEFAULT_USERS:
            username = user_data["username"]
            try:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "email": user_data["email"],
                        "first_name": user_data["first_name"],
                        "last_name": user_data["last_name"],
                        "is_staff": user_data["is_staff"],
                        "is_superuser": user_data["is_superuser"],
                        "is_active": True,
                    },
                )

                # Always set the password (for e-signature support)
                user.set_password(user_data["password"])
                user.is_active = True
                user.save()

                # Set role if the user model has a role field
                if hasattr(user, "role") and user_data.get("role"):
                    user.role = user_data["role"]
                    user.save(update_fields=["role"])

                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"  Created user: {username}")
                    )
                else:
                    updated_count += 1
                    self.stdout.write(f"  Updated user: {username}")

            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"  Failed to create {username}: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone: {created_count} created, {updated_count} updated."
            )
        )
