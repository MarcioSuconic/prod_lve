from django.apps import AppConfig


class ProductionInputConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.productions.production_input"
    verbose_name = "Insumos da Produção"