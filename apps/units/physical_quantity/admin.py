from django.contrib import admin

# Register your models here.
from apps.units.physical_quantity.models import PhysicalQuantity

admin.site.register(PhysicalQuantity)