# apps/products/product_x_sub_product/models.py
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models

from apps.sub_products.sub_product.models import SubProduct
from apps.products.product.models import Product


class Product_x_Sub_Product(models.Model):
    """
    Produtos x Sub Produtos.

    Registra os Sub Produtos com seu percentual de composição e o
    timing de produção (quando cada sub-produto começa/termina em
    relação à produção ou a outro sub-produto).
    """

    product = models.ForeignKey(
        Product,
        verbose_name="Produto",
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )
    sub_product = models.ForeignKey(
        SubProduct,
        verbose_name="Sub Produto",
        on_delete=models.PROTECT,
        null=False,
        blank=False,
    )
    composition_percentage = models.DecimalField(
        verbose_name="percentual do padeiro",
        max_digits=10,
        decimal_places=6,
    )

    # --- timing de produção ---

    # Ponto de referência (só 1 pode ser True, ou nenhum):
    # - at_start=True   → referência é o INÍCIO do sub-produto apontado
    # - at_finish=True  → referência é o FIM do sub-produto apontado
    # - after_to=True   → referência é DEPOIS do fim do sub-produto apontado
    # - nenhum ativo    → referência é o INÍCIO da produção
    at_start = models.BooleanField(
        verbose_name="referência é o início do sub-produto",
        default=False,
    )
    at_finish = models.BooleanField(
        verbose_name="referência é o fim do sub-produto",
        default=False,
    )
    after_to = models.BooleanField(
        verbose_name="referência é depois do fim do sub-produto",
        default=False,
    )

    # Sub-produto de referência (obrigatório se algum booleano ativo)
    relative_to = models.ForeignKey(
        "self",
        verbose_name="sub-produto de referência",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="relatives",
    )

    # Ajuste temporal aplicado à referência
    elapsed_time = models.DurationField(
        verbose_name="tempo decorrido",
        default=timedelta(0),
        help_text="Tempo somado ou subtraído do ponto de referência.",
    )
    elapsed_signal = models.CharField(
        verbose_name="sinal do tempo decorrido",
        max_length=1,
        choices=(
            ("+", "Somar"),
            ("-", "Subtrair"),
        ),
        default="+",
    )

    created_at = models.DateTimeField(
        verbose_name="criado em", auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name="atualizado em", auto_now=True,
    )
    active = models.BooleanField(verbose_name="ativo", default=True)

    class Meta:
        ordering = ["product", "sub_product", "composition_percentage"]
        db_table = "lve_pro_product_x_sub_product"
        verbose_name = "Produto X Sub-Produto"
        verbose_name_plural = "Produtos X Sub-Produtos"

    def __str__(self):
        return (
            f"{self.product} {self.sub_product} "
            f"{self.composition_percentage}"
        )

    # ------------------------------------------------------------------
    # Validações
    # ------------------------------------------------------------------
    def clean(self):
        # 1. Só um dos 3 booleanos pode estar ativo
        ativos = sum([self.at_start, self.at_finish, self.after_to])
        if ativos > 1:
            raise ValidationError(
                "Só um dos booleanos (at_start, at_finish, after_to) "
                "pode estar ativo por vez."
            )

        # 2. Se algum booleano ativo, relative_to é obrigatório
        if ativos == 1 and not self.relative_to:
            raise ValidationError({
                "relative_to": (
                    "Quando um booleano de referência está ativo, "
                    "é obrigatório informar o sub-produto de referência."
                ),
            })

        # 3. Nenhum booleano ativo → relative_to deve ser nulo
        if ativos == 0 and self.relative_to:
            raise ValidationError({
                "relative_to": (
                    "Sem booleano de referência ativo, "
                    "relative_to deve ficar vazio (referência é o "
                    "início da produção)."
                ),
            })

        # 4. relative_to não pode apontar pra si mesmo
        if self.relative_to and self.pk and self.relative_to.pk == self.pk:
            raise ValidationError({
                "relative_to": "O sub-produto não pode referenciar a si mesmo.",
            })

        # 5. product e relative_to devem pertencer ao mesmo produto
        if (
            self.relative_to
            and self.product_id
            and self.relative_to.product_id != self.product_id
        ):
            raise ValidationError({
                "relative_to": (
                    "O sub-produto de referência deve pertencer "
                    "ao mesmo produto."
                ),
            })

        # 6. after_to + sinal "-" não faz sentido (começaria antes do fim)
        if self.after_to and self.elapsed_signal == "-":
            raise ValidationError({
                "elapsed_signal": (
                    "after_to com sinal '-' faria o passo começar antes "
                    "do sub-produto de referência terminar. "
                    "Use sinal '+' ou remova after_to."
                ),
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)