from django.apps import AppConfig


class PendingProductionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.productions.pending_production"
    verbose_name = "Produções Pendentes"
