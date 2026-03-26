from django.apps import AppConfig


class SafetyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "safety"
    verbose_name = "Pharmacovigilance & Safety"

    def ready(self):
        import safety.signals  # noqa: F401
