from django.db import models
from apps.stories.store.models import Store

# Create your models here.

class ElectricPower_x_Store(models.Model):
    store = models.ForeignKey(Store, verbose_name="estabelecimento")
    fare_amount_kwh = models.DecimalField(verbose_name="valor da tarifa da energia elétrica", max_digits=12, decimal_places=2)    
    date = models.DateField(verbose_name="data referencial")
    