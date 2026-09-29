from django.contrib import admin
from .models import RegisterProductionProducts, FeedBackProductionProducts


@admin.register(RegisterProductionProducts)
class RegisterProductionProductsAdmin(admin.ModelAdmin):
    list_display = ("product", "date_production", "quantity", "unit", "done")
    list_filter = ("done", "product")
    date_hierarchy = "date_production"


@admin.register(FeedBackProductionProducts)
class FeedBackProductionProductsAdmin(admin.ModelAdmin):
    list_display = ("register_production_product",)
