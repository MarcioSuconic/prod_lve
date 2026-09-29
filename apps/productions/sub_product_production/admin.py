from django.contrib import admin
from .models import RegisterProductionSubProducts, FeedBackProductionSubProducts


@admin.register(RegisterProductionSubProducts)
class RegisterProductionSubProductsAdmin(admin.ModelAdmin):
    list_display = ("sub_product", "store", "date_production", "quantity", "unit", "done")
    list_filter = ("store", "done", "sub_product")
    date_hierarchy = "date_production"


@admin.register(FeedBackProductionSubProducts)
class FeedBackProductionSubProductsAdmin(admin.ModelAdmin):
    list_display = ("register_production_sub_product",)
