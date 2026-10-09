# apps/products/product/services.py
"""
Escalonamento de receita: dada uma quantidade de produto a produzir,
calcula quanto de cada insumo é necessário.
"""

from decimal import Decimal
from dataclasses import dataclass
from datetime import timedelta

from apps.food_ingredients.food_ingredient.models import FoodIngredient
from apps.food_ingredients.food_ingredient.services import convert
from apps.food_ingredients.food_ingredient_purchase.models import (
    FoodIngredientPurchase,
)

from apps.recipe.execution_operation_base_recipe.models import (
    ExecutionOperationBaseRecipe,
)
from apps.units.unit.models import Unit
from apps.units.unit.services import convert_same_quantity

from apps.stories.electric_power_x_store.models import ElectricPower_x_Store
from apps.stories.average_hourly_wage_x_store.models import (
    AverageHourlyWage_x_Store,
)

from apps.products.product_x_sub_product.models import Product_x_Sub_Product

from .models import Product


class ScalingError(Exception):
    """Erro de escalonamento de receita."""


@dataclass
class ScaledIngredient:
    food_ingredient: FoodIngredient
    quantity: Decimal
    unit: Unit
    unincorporated: bool


def scale_product(
    product: Product,
    target_quantity: Decimal,
    target_unit: Unit,
) -> list[ScaledIngredient]:
    """
    Calcula os insumos necessários para produzir `target_quantity` do produto.

    Levanta ScalingError se faltar configuração (receita sem tamanho, densidade
    ausente, unidade incompatível).
    """
    if target_quantity <= 0:
        raise ScalingError("A quantidade alvo deve ser maior que zero.")

    links = (
        Product_x_Sub_Product.objects
        .filter(product=product, active=True)
        .select_related(
            "sub_product",
            "sub_product__base_recipe",
            "sub_product__base_recipe__unit_size",
        )
    )
    if not links.exists():
        raise ScalingError(f"Produto '{product}' não tem subprodutos ativos.")

    # Acumula por insumo para consolidar repetidos
    acumulado: dict[int, ScaledIngredient] = {}

    for link in links:
        sub_product = link.sub_product
        base_recipe = sub_product.base_recipe

        if not base_recipe.size or base_recipe.size <= 0:
            raise ScalingError(
                f"Receita base '{base_recipe}' não tem tamanho definido."
            )

        # Quanto deste subproduto o produto final requer
        sub_qty = target_quantity * (
            link.composition_percentage / Decimal("100")
        )

        # Converte sub_qty (target_unit) para a unidade da receita base
        sub_qty_in_recipe_unit = convert_same_quantity(
            sub_qty,
            target_unit,
            base_recipe.unit_size,
        )

        scale = sub_qty_in_recipe_unit / base_recipe.size

        steps = (
            ExecutionOperationBaseRecipe.objects
            .filter(base_recipe=base_recipe, food_ingredient__isnull=False)
            .select_related("food_ingredient", "unidade_qtde_food_ingredient")
        )

        for step in steps:
            ingredient = step.food_ingredient
            required_qty_in_step_unit = step.qtde_food_ingredient * scale

            # Converte para a unidade padrão do insumo
            target_ing_unit = ingredient.unit
            required_qty_in_ingredient_unit = convert(
                required_qty_in_step_unit,
                step.unidade_qtde_food_ingredient,
                target_ing_unit,
                food_ingredient=ingredient,
            )

            existing = acumulado.get(ingredient.id)
            if existing:
                existing.quantity += required_qty_in_ingredient_unit
            else:
                acumulado[ingredient.id] = ScaledIngredient(
                    food_ingredient=ingredient,
                    quantity=required_qty_in_ingredient_unit,
                    unit=target_ing_unit,
                    unincorporated=step.incorporation_percentage,
                )

    return sorted(
        acumulado.values(),
        key=lambda x: x.food_ingredient.food_ingredient,
    )


@dataclass
class IngredientCost:
    food_ingredient: FoodIngredient
    quantity: Decimal
    unit: Unit
    price_per_unit: Decimal   # preço por 1 unidade do insumo
    subtotal: Decimal         # quantity * price_per_unit


def _price_per_unit(
    ingredient: FoodIngredient,
    purchase: FoodIngredientPurchase,
) -> Decimal:
    """
    Preço por 1 unidade padrão do insumo, derivado da compra.

    Ex.: compra de 1000 gr por R$ 6,00 e insumo em kg →
         converte 1000 gr para 1 kg, depois 6,00 / 1 = 6,00 R$/kg.
    """
    qty_in_ingredient_unit = convert(
        purchase.quantity,
        purchase.unit,
        ingredient.unit,
        food_ingredient=ingredient,
    )
    if not qty_in_ingredient_unit:
        return Decimal("0")
    return purchase.total_price / qty_in_ingredient_unit


def ingredient_cost(
    product: Product,
    target_quantity: Decimal,
    target_unit: Unit,
) -> list[IngredientCost]:
    """
    Calcula o custo dos insumos para produzir `target_quantity` do produto.

    Usa a compra mais recente de cada insumo como referência de preço.
    Levanta ScalingError se algum insumo não tiver compra cadastrada.
    """
    scaled = scale_product(product, target_quantity, target_unit)
    result: list[IngredientCost] = []

    for s in scaled:
        purchase = (
            s.food_ingredient.purchases
            .order_by("-date", "-created_at")
            .first()
        )
        if purchase is None:
            raise ScalingError(
                f"Insumo '{s.food_ingredient}' não tem nenhuma compra cadastrada."
            )

        price = _price_per_unit(s.food_ingredient, purchase)
        result.append(IngredientCost(
            food_ingredient=s.food_ingredient,
            quantity=s.quantity,
            unit=s.unit,
            price_per_unit=price,
            subtotal=s.quantity * price,
        ))

    return result


# ---------------------------------------------------------------------------
# Fase 2 — energia e salário
# ---------------------------------------------------------------------------

@dataclass
class EnergyCost:
    total_kwh: Decimal
    tariff_per_kwh: Decimal
    total: Decimal
    steps: list[dict]


@dataclass
class LaborCost:
    total_hours: Decimal
    hourly_wage: Decimal
    total: Decimal


@dataclass
class FullCost:
    ingredients: list[IngredientCost]
    ingredients_total: Decimal
    energy: EnergyCost | None
    labor: LaborCost | None
    grand_total: Decimal


def _elapsed_seconds(td: timedelta) -> Decimal:
    return Decimal(str(td.total_seconds()))


def _scale_factor_for_subproduct(
    link, target_quantity, target_unit,
) -> Decimal:
    """Fator de escala do subproduto em relação ao tamanho da receita base."""
    base_recipe = link.sub_product.base_recipe
    sub_qty = target_quantity * (
        link.composition_percentage / Decimal("100")
    )
    sub_qty_in_recipe_unit = convert_same_quantity(
        sub_qty, target_unit, base_recipe.unit_size,
    )
    return sub_qty_in_recipe_unit / base_recipe.size


def full_cost(
    product: Product,
    target_quantity: Decimal,
    target_unit: Unit,
) -> FullCost:
    """
    Custo completo: insumos + energia + salário.

    Energia: por passo com maquinário, `potência(kW) × tempo(h) × tarifa`.
    Salário: tempo total de execução × valor médio da hora trabalhada.
    """
    # 1. Insumos (já temos)
    ingredients = ingredient_cost(product, target_quantity, target_unit)
    ingredients_total = sum(
        (c.subtotal for c in ingredients), Decimal("0"),
    )

    # 2. Unidade alvo de potência (kW). Se não existir, energia fica indisponível.
    kilowatt = Unit.objects.filter(
        physical_quantity__slug="potencia", unit__iexact="kilowatt"
    ).first()

    # 3. Acumula tempo total e energia por passo
    links = (
        Product_x_Sub_Product.objects
        .filter(product=product, active=True)
        .select_related(
            "sub_product",
            "sub_product__base_recipe",
            "sub_product__base_recipe__unit_size",
        )
    )

    total_seconds = Decimal("0")
    total_kwh = Decimal("0")
    energy_steps: list[dict] = []

    for link in links:
        base_recipe = link.sub_product.base_recipe
        if not base_recipe.size or base_recipe.size <= 0:
            raise ScalingError(
                f"Receita base '{base_recipe}' não tem tamanho definido."
            )
        scale = _scale_factor_for_subproduct(
            link, target_quantity, target_unit,
        )

        steps = (
            ExecutionOperationBaseRecipe.objects
            .filter(base_recipe=base_recipe)
            .select_related("machinery", "machinery__unit_power")
        )

        for step in steps:
            step_seconds = _elapsed_seconds(step.elapsed_time) * scale
            total_seconds += step_seconds

            if step.machinery and kilowatt:
                power_kw = convert_same_quantity(
                    step.machinery.qtde_power,
                    step.machinery.unit_power,
                    kilowatt,
                )
                step_hours = step_seconds / Decimal("3600")
                step_kwh = power_kw * step_hours
                total_kwh += step_kwh
                energy_steps.append({
                    "step": step.description_execution,
                    "machinery_code": step.machinery.code,
                    "machinery_name": step.machinery.machinery,
                    "power_kw": str(power_kw),
                    "hours": str(step_hours),
                    "kwh": str(step_kwh),
                })

    # 4. Tarifa de energia (última registrada para a loja)
    store = product.store
    tariff_row = (
        ElectricPower_x_Store.objects
        .filter(store=store)
        .order_by("-date", "-created_at")
        .first()
    )
    if tariff_row is None:
        energy = None
    else:
        energy = EnergyCost(
            total_kwh=total_kwh,
            tariff_per_kwh=tariff_row.fare_amount_kwh,
            total=total_kwh * tariff_row.fare_amount_kwh,
            steps=energy_steps,
        )

    # 5. Salário (última média registrada para a loja)
    wage_row = (
        AverageHourlyWage_x_Store.objects
        .filter(store=store)
        .order_by("-date", "-created_at")
        .first()
    )
    if wage_row is None:
        labor = None
    else:
        hours = total_seconds / Decimal("3600")
        labor = LaborCost(
            total_hours=hours,
            hourly_wage=wage_row.average_hourly_wage,
            total=hours * wage_row.average_hourly_wage,
        )

    grand_total = ingredients_total
    if energy:
        grand_total += energy.total
    if labor:
        grand_total += labor.total

    return FullCost(
        ingredients=ingredients,
        ingredients_total=ingredients_total,
        energy=energy,
        labor=labor,
        grand_total=grand_total,
    )
    
# =========================================================================
# Cronograma de produção (timing dos sub-produtos)
# =========================================================================
from datetime import datetime, timedelta as _td
from decimal import Decimal as _Dec


class ScheduleError(Exception):
    """Erro no cálculo de cronograma."""


def calcular_cronograma(
    product_id: int,
    data_inicio: datetime,
) -> dict:
    """
    Calcula o cronograma de produção de um produto.

    Cada vínculo (Product_x_Sub_Product) pode ter um timing:
      - at_start=True   → referência é o início do sub-produto apontado
      - at_finish=True  → referência é o fim do sub-produto apontado
      - after_to=True   → referência é depois do fim do sub-produto
      - nenhum          → referência é o início da produção

    O `elapsed_time` é somado ou subtraído (conforme `elapsed_signal`)
    do ponto de referência.
    """
    from apps.products.product_x_sub_product.models import (
        Product_x_Sub_Product,
    )
    from apps.recipe.execution_operation_base_recipe.models import (
        ExecutionOperationBaseRecipe,
    )

    vinculos = list(
        Product_x_Sub_Product.objects
        .filter(product_id=product_id, active=True)
        .select_related(
            "sub_product",
            "sub_product__base_recipe",
            "relative_to",
            "relative_to__sub_product",
        )
    )

    if not vinculos:
        raise ScheduleError("Produto não tem sub-produtos ativos.")

    # ---- 1. Duração de cada sub-produto ----
    duracao_por_vinculo = {}
    for v in vinculos:
        receita = v.sub_product.base_recipe
        execs = ExecutionOperationBaseRecipe.objects.filter(
            base_recipe=receita,
        )
        if not execs.exists():
            raise ScheduleError(
                f"Sub-produto '{v.sub_product}' não tem execuções."
            )
        max_seg = 0
        for ex in execs:
            el = ex.elapsed_time.total_seconds()
            et = ex.execution_time.total_seconds()
            if el + et > max_seg:
                max_seg = el + et
        duracao_por_vinculo[v.id] = _td(seconds=max_seg)

    # ---- 2. Valida ciclos ----
    _validar_ciclos(vinculos)

    # ---- 3. Ordena topologicamente ----
    ordem = _topological_sort(vinculos)

    # ---- 4. Calcula horários ----
    horarios = {}

    for v in ordem:
        duracao = duracao_por_vinculo[v.id]

        if v.at_start or v.at_finish or v.after_to:
            if not v.relative_to:
                raise ScheduleError(
                    f"Vínculo {v} tem booleano ativo sem relative_to."
                )
            ref = horarios.get(v.relative_to.id)
            if ref is None:
                raise ScheduleError(
                    f"Sub-produto '{v.sub_product}' depende de "
                    f"'{v.relative_to.sub_product}', que não foi calculado."
                )
            if v.at_start:
                ref_dt = ref["inicio"]
            else:
                # at_finish ou after_to → referência é o fim
                ref_dt = ref["fim"]
        else:
            ref_dt = data_inicio

        # Aplica elapsed_time com sinal
        if v.elapsed_signal == "-":
            ponto = ref_dt - v.elapsed_time
        else:
            ponto = ref_dt + v.elapsed_time

        # Calcula início/fim
        if v.at_finish:
            fim = ponto
            inicio = fim - duracao
        else:
            inicio = ponto
            fim = inicio + duracao

        horarios[v.id] = {"inicio": inicio, "fim": fim}

    # ---- 5. Monta resposta ----
    data_fim = max(h["fim"] for h in horarios.values())
    duracao_total = data_fim - data_inicio

    passos = []
    for v in ordem:
        h = horarios[v.id]
        passos.append({
            "sub_product": str(v.sub_product),
            "sub_product_id": v.sub_product_id,
            "duracao_h": str(
                _Dec(str(duracao_por_vinculo[v.id].total_seconds()))
                / _Dec("3600")
            ),
            "inicio": h["inicio"].isoformat(),
            "fim": h["fim"].isoformat(),
            "at_start": v.at_start,
            "at_finish": v.at_finish,
            "after_to": v.after_to,
            "relative_to": (
                str(v.relative_to.sub_product) if v.relative_to else None
            ),
            "elapsed_time": str(
                _Dec(str(v.elapsed_time.total_seconds())) / _Dec("3600")
            ),
            "elapsed_signal": v.elapsed_signal,
        })

    return {
        "product_id": product_id,
        "data_inicio": data_inicio.isoformat(),
        "data_fim": data_fim.isoformat(),
        "duracao_total_h": str(
            _Dec(str(duracao_total.total_seconds())) / _Dec("3600")
        ),
        "passos": passos,
    }


def _validar_ciclos(vinculos):
    """Levanta ScheduleError se houver ciclo."""
    mapa = {v.id: v for v in vinculos}
    for v in vinculos:
        visitados = set()
        atual = v
        while atual and atual.relative_to:
            if atual.relative_to.id in visitados:
                raise ScheduleError(
                    f"Ciclo detectado envolvendo '{v.sub_product}'."
                )
            visitados.add(atual.id)
            atual = mapa.get(atual.relative_to.id)


def _topological_sort(vinculos):
    """Ordena por dependência (sem dependência primeiro)."""
    mapa = {v.id: v for v in vinculos}
    ordenados = []
    visitados = set()

    def visitar(v):
        if v.id in visitados:
            return
        if v.relative_to:
            ref = mapa.get(v.relative_to.id)
            if ref:
                visitar(ref)
        visitados.add(v.id)
        ordenados.append(v)

    for v in vinculos:
        visitar(v)

    return ordenados