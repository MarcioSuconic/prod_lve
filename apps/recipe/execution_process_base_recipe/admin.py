from django.contrib import admin
from .models import ExecutionOperationBaseRecipe


@admin.register(ExecutionOperationBaseRecipe)
class ExecutionProcessBaseRecipeAdmin(admin.ModelAdmin):
    list_display = (
        "base_recipe",
        "stage_execution",
        "operation_execution",
        "food_ingredient",
        "qtde_food_ingredient",
        "unidade_qtde_food_ingredient",
        "elapsed_time",
    )
    list_filter = ("base_recipe", "stage_execution", "operation_execution")
    search_fields = ("description_execution",)
    autocomplete_fields = ("base_recipe", "food_ingredient", "unidade_qtde_food_ingredient")
