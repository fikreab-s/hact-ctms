from django.apps import AppConfig


class LabConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lab"
    verbose_name = "Laboratory & Biomarker Data"

    def ready(self):
        import lab.signals  # noqa: F401
