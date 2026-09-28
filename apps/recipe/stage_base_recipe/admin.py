from django.contrib import admin
from .models import StageBaseRecipe


@admin.register(StageBaseRecipe)
class StageBaseRecipeAdmin(admin.ModelAdmin):
    list_display = ("stage_base_recipe", "active")
    list_filter = ("active",)
    search_fields = ("stage_base_recipe",)
