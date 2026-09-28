from django.contrib import admin
from .models import BaseRecipe


@admin.register(BaseRecipe)
class BaseRecipeAdmin(admin.ModelAdmin):
    list_display = ("base_recipe", "size", "unit_size", "active")
    list_filter = ("active", "unit_size")
    search_fields = ("base_recipe",)