from django.apps import AppConfig


class IntegrationsConfig(AppConfig):
    """
    HACT CTMS — External Systems Integration App.
    Provides connectors for OpenClinica, Nextcloud, ERPNext, and SENAITE.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "integrations"
    verbose_name = "External System Integrations"
