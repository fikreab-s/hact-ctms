from django.apps import AppConfig


class OutputsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "outputs"
    verbose_name = "Reporting & Data Exports"

    def ready(self):
        import outputs.signals  # noqa: F401
