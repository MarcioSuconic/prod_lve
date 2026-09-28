from django.contrib import admin
from .models import ExecutionProcessBaseRecipe


@admin.register(ExecutionProcessBaseRecipe)
class ExecutionProcessBaseRecipeAdmin(admin.ModelAdmin):
    list_display = (
        "base_recipe",
        "stage_execution",
        "process_execution",
        "food_ingredient",
        "qtde_food_ingredient",
        "unidade_qtde_food_ingredient",
        "elapsed_time",
    )
    list_filter = ("base_recipe", "stage_execution", "process_execution")
    search_fields = ("description_execution",)
    autocomplete_fields = ("base_recipe", "food_ingredient", "unidade_qtde_food_ingredient")
