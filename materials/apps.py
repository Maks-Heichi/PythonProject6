from django.apps import AppConfig


class MaterialsConfig(AppConfig):
    """Приложение курсов и уроков."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "materials"
    verbose_name = "Материалы"
