from django.db import models, transaction

from apps.units.physical_quantity.models import PhysicalQuantity


class Unit(models.Model):
    unit = models.CharField(
        verbose_name="unidade física",
        max_length=48,
        blank=False,
        null=False,
    )
    physical_quantity = models.ForeignKey(
        PhysicalQuantity,
        verbose_name="grandeza física",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name="units",
    )
    symbol = models.CharField(
        verbose_name="símbolo da unidade",
        max_length=3,
        blank=False,
        null=False,
    )
    is_benchmark = models.BooleanField(
        verbose_name="a unidade é a referencial",
        default=False,
    )
    conversion_factor = models.DecimalField(
        verbose_name="fator de conversão para a unidade referencial",
        max_digits=20,
        decimal_places=10,
        default=1,
        help_text=(
            "Quantas unidades referenciais (benchmark) equivalem a 1 desta unidade. "
            "Ex.: se a benchmark de Massa é o grama, então 1 kg tem fator 1000. "
            "A própria unidade benchmark deve ter fator 1."
        ),
    )

    class Meta:
        db_table = "lve_uni_unit"
        verbose_name = "Unidade Física"
        verbose_name_plural = "Unidades Físicas"
        ordering = ["physical_quantity", "unit"]
        constraints = [
            models.UniqueConstraint(
                fields=["physical_quantity"],
                condition=models.Q(is_benchmark=True),
                name="unique_benchmark_per_physical_quantity",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(is_benchmark=False)
                    | models.Q(is_benchmark=True, conversion_factor=1)
                ),
                name="benchmark_unit_must_have_factor_one",
            ),
        ]

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.is_benchmark:
                Unit.objects.filter(
                    physical_quantity=self.physical_quantity,
                    is_benchmark=True,
                ).exclude(pk=self.pk).update(is_benchmark=False)
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.physical_quantity} - {self.symbol}"