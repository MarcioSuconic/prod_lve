# apps/audit/services.py
from decimal import Decimal

from apps.food_ingredients.food_ingredient.models import FoodIngredient
from apps.products.product_x_sub_product.models import Product_x_Sub_Product
from apps.recipe.base_recipe.models import BaseRecipe
from apps.recipe.base_recipe.services import calcular_balanco_massa


def auditar_produtos_sem_100() -> list[dict]:
    """Lista produtos cuja soma de composition_percentage ≠ 100%."""
    produtos = set(
        Product_x_Sub_Product.objects
        .filter(active=True)
        .values_list("product_id", flat=True)
    )
    problemas = []
    for pid in produtos:
        links = Product_x_Sub_Product.objects.filter(
            product_id=pid, active=True,
        ).select_related("product")
        total = sum((l.composition_percentage for l in links), Decimal("0"))
        if total != Decimal("100"):
            problemas.append({
                "product_id": pid,
                "product": links.first().product.product,
                "soma": str(total),
                "faltam": str(Decimal("100") - total),
            })
    return problemas


def auditar_insumos_sem_densidade() -> list[dict]:
    """Lista insumos de volume sem densidade cadastrada."""
    insumos = FoodIngredient.objects.filter(
        unit__physical_quantity__slug="volume",
        active=True,
    ).prefetch_related("densities")
    problemas = []
    for i in insumos:
        if not i.densities.exists():
            problemas.append({
                "food_ingredient_id": i.id,
                "food_ingredient": i.food_ingredient,
                "unit": i.unit.symbol,
            })
    return problemas


def auditar_receitas_com_balanco_ruim() -> list[dict]:
    """Lista receitas cujo balanço de massa é 'erro' ou 'suspeito'."""
    problemas = []
    for r in BaseRecipe.objects.filter(active=True):
        b = calcular_balanco_massa(r)
        if b["classificacao"] in ("erro", "suspeito"):
            problemas.append({
                "receita_id": r.id,
                "receita": r.base_recipe,
                "size": b["size"],
                "peso_input_g": b["peso_input_g"],
                "diferenca_g": b["diferenca_g"],
                "diferenca_pct": b["diferenca_pct"],
                "classificacao": b["classificacao"],
            })
    return problemas


def auditar_sistema() -> dict:
    """Roda todas as auditorias e devolve o resultado."""
    return {
        "produtos_sem_100": auditar_produtos_sem_100(),
        "insumos_sem_densidade": auditar_insumos_sem_densidade(),
        "receitas_com_balanco_ruim": auditar_receitas_com_balanco_ruim(),
    }