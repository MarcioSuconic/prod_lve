from django.db import models


class PhysicalQuantity(models.Model):
    physical_quantity = models.CharField(
        max_length=48,
        verbose_name="grandeza física",
    )
    slug = models.SlugField(
        max_length=48,
        unique=True,
        verbose_name="identificador canônico",
        help_text=(
            "Identificador estável usado no código. "
            "Ex.: massa, volume, temperatura. Não editar depois de definido."
        ),
    )
    class Meta:
        db_table = "lve_uni_physical_quantity"
        verbose_name = "Grandeza Física"
        verbose_name_plural = "Grandezas Físicas"
        ordering = ["physical_quantity"]

    def __str__(self):
        return self.physical_quantity