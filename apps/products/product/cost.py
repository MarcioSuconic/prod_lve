# apps/products/product/cost.py
"""
Cálculo de custo unitário de um Produto.

Estratégia:
  1. Para cada sub-produto do produto (via Product_x_Sub_Product):
     - Calcula o custo da receita base do sub-produto
       (via base_recipe.services.calcular_custo_receita)
     - Converte para custo por unidade de tamanho da receita
     - Multiplica pela quantidade que entra no produto
       (peso_do_produto × composition_percentage / 100)
  2. Soma os custos dos sub-produtos.
  3. Aplica o markup_default da sub-categoria do produto.
  4. Arredonda o preço final pela regra PriceRounder.
"""

from datetime import date
from decimal import Decimal

from apps.recipe.base_recipe.services import calcular_custo_receita

from .models import Product


# ---------------------------------------------------------------------------
# Arredondamento do preço de venda
# ---------------------------------------------------------------------------
class PriceRounder:
    """
    Arredonda o preço de venda para o próximo múltiplo de 0,50
    e soma mais 0,50.

    Exemplos:
        2,00 → 2,50
        2,01 → 3,00
        2,50 → 3,00
        2,51 → 3,50
        5,99 → 6,50
    """

    ACRESCIMO = Decimal("0.50")

    @classmethod
    def round(cls, pv) -> Decimal:
        pv = Decimal(str(pv))
        sobra = pv % 1

        if sobra == 0:
            return Decimal(int(pv)) + cls.ACRESCIMO
        elif sobra <= Decimal("0.50"):
            return Decimal(int(pv)) + Decimal("0.50") + cls.ACRESCIMO
        else:
            return Decimal(int(pv)) + Decimal("1.00") + cls.ACRESCIMO


# ---------------------------------------------------------------------------
# Cálculo principal
# ---------------------------------------------------------------------------
def calcular_custo_produto(
    produto: Product,
    data_referencia: date | None = None,
) -> dict:
    """
    Calcula o custo unitário de um produto e o preço de venda sugerido.
    """
    data_ref = data_referencia or date.today()

    peso_produto = produto.product_weight_or_volume
    unidade_produto = produto.unit_weight_or_volume

    composicoes = (
        produto.product_x_sub_product_set
        .select_related(
            "sub_product",
            "sub_product__base_recipe",
            "sub_product__base_recipe__unit_size",
        )
        .filter(active=True)
    )

    sub_produtos = []
    custo_produto = Decimal("0")

    for comp in composicoes:
        sub = comp.sub_product
        receita = sub.base_recipe

        resultado_receita = calcular_custo_receita(
            receita, data_referencia=data_ref,
        )
        custo_receita = Decimal(resultado_receita["custo_total"])

        size_receita = Decimal(resultado_receita["size"])
        unit_size_sym = resultado_receita["unit_size"]

        if size_receita == 0:
            custo_por_unidade = Decimal("0")
        else:
            custo_por_unidade = custo_receita / size_receita

        pct = comp.composition_percentage / Decimal("100")
        qtd_no_produto = peso_produto * pct

        qtd_na_unidade_receita = _converter_mesma_grandeza(
            qtd_no_produto, unidade_produto, receita.unit_size,
        )

        custo_no_produto = custo_por_unidade * qtd_na_unidade_receita
        custo_produto += custo_no_produto

        sub_produtos.append({
            "sub_product": sub.sub_product,
            "sub_product_id": sub.id,
            "base_recipe": receita.base_recipe,
            "base_recipe_id": receita.id,
            "composition_percentage": str(comp.composition_percentage),
            "recipe_size": str(size_receita),
            "recipe_unit": unit_size_sym,
            "recipe_cost_total": str(custo_receita),
            "recipe_cost_per_unit": str(custo_por_unidade),
            "quantity_in_product": str(qtd_no_produto),
            "unit_in_product": unidade_produto.symbol,
            "quantity_in_recipe_unit": str(qtd_na_unidade_receita),
            "recipe_unit_for_product": receita.unit_size.symbol,
            "cost_in_product": str(custo_no_produto),
        })

    sub_categoria = produto.sub_category
    markup_default = (
        sub_categoria.markup_default if sub_categoria else Decimal("0")
    )

    fator = Decimal("1") + (markup_default / Decimal("100"))
    preco_bruto = custo_produto * fator

    preco_final = PriceRounder.round(preco_bruto)

    return {
        "product": produto.product,
        "product_id": produto.id,
        "name_menu": produto.name_menu,
        "store": str(produto.store),
        "weight": str(peso_produto),
        "unit": unidade_produto.symbol,
        "data_referencia": data_ref.isoformat(),
        "sub_products": sub_produtos,
        "custo_produto": str(custo_produto),
        "markup_default": str(markup_default),
        "preco_bruto": str(preco_bruto),
        "preco_sugerido": str(preco_final),
    }


def _converter_mesma_grandeza(qtd, from_unit, to_unit) -> Decimal:
    """Converte quantidade entre unidades da mesma grandeza."""
    if from_unit.physical_quantity_id == to_unit.physical_quantity_id:
        from apps.units.unit.services import convert_same_quantity
        return convert_same_quantity(qtd, from_unit, to_unit)
    return qtd