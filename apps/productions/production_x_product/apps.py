from django.apps import AppConfig


class ProductionXProductConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.productions.production_x_product"
    verbose_name = "Produção x Produto"
