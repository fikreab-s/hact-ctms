from django.apps import AppConfig


class OpsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ops"
    verbose_name = "Operational & Site Management"

    def ready(self):
        import ops.signals  # noqa: F401
