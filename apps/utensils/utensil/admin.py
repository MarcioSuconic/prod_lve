from django.contrib import admin

from .models import Utensil, Utensil


@admin.register(Utensil)
class UtensilAdmin(admin.ModelAdmin):
    list_display = ("code", "utensil", "store", "active")
    list_filter = ("store", "active")
    search_fields = ("utensil", "code")

