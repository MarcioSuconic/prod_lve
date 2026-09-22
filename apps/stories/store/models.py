from django.db import models

# Create your models here.

class Store(models.Model):
    nome_estabelecimento = models.CharField(verbose_name="nome do estabelecimento", max_length=120, blank=False, null=False)
    id_store = models.IntegerField(verbose_name="ID da loja no app Principal")
    