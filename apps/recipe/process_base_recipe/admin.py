from django.contrib import admin
from .models import ProcessBaseRecipe


@admin.register(ProcessBaseRecipe)
class ProcessBaseRecipeAdmin(admin.ModelAdmin):
    list_display = ("process_base_recipe", "active")
    list_filter = ("active",)
    search_fields = ("process_base_recipe",)
