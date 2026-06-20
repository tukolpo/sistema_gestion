from django.apps import AppConfig


class TrabajadoresExtConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "trabajadores_ext"
    verbose_name = "Trabajadores — QR y auditoría"

    def ready(self):
        import trabajadores_ext.signals  # noqa: F401
