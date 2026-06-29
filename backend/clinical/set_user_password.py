"""
Set Django user password to match Keycloak credentials.

When using Keycloak SSO, Django doesn't store user passwords.
This script syncs the password so e-signature (check_password) works locally.

Usage:
    docker exec hact-django-api python manage.py shell < clinical/set_user_password.py
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hact_ctms.settings")
try:
    django.setup()
except:
    pass

from django.contrib.auth import get_user_model

User = get_user_model()

# Set password for all EDC users
users_updated = []
for user in User.objects.all():
    # Set the Django password to match the Keycloak password
    # For testing: set it to the username (matching Keycloak setup)
    user.set_password(user.username)
    user.save()
    users_updated.append(user.username)
    print(f"  Set password for '{user.username}' → '{user.username}'")

print(f"\n✅ Updated {len(users_updated)} users.")
print("E-signature will now work with your Keycloak password (same as username).")
