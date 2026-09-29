from django.contrib import admin
from .models import OperationBaseRecipe


@admin.register(OperationBaseRecipe)
class ProcessBaseRecipeAdmin(admin.ModelAdmin):
    list_display = ("operation_base_recipe", "active")
    list_filter = ("active",)
    search_fields = ("operation_base_recipe",)
