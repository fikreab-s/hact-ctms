from django.apps import AppConfig


class ClinicalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "clinical"
    verbose_name = "Clinical Study & Data Collection"

    def ready(self):
        import clinical.signals  # noqa: F401
