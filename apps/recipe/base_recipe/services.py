# apps/recipe/base_recipe/services.py
"""
Cálculo de custo de uma receita base.

Estratégia:
  1. Custo de insumos: para cada passo com insumo, converte a quantidade
     para a unidade da compra mais recente (via services.convert, que trata
     densidade e porção), multiplica pelo unit_price da compra.
  2. Custo de energia: para cada passo com maquinário, potência (kW) ×
     tempo (h) × tarifa (R$/kWh) vigente na data.
  3. Custo de mão de obra: tempo (h) × salário/hora vigente na data.

Conversão de potência:
  O campo `Machinery.qtde_power` está na unidade `unit_power` (ex.: W, kW).
  A tarifa é em R$/kWh, então convertemos a potência para kW antes de
  multiplicar. A conversão usa `convert_same_quantity`, que passa pela
  benchmark da grandeza (W, no caso de potência).
"""

from datetime import date
from decimal import Decimal

from apps.food_ingredients.food_ingredient_purchase.models import (
    FoodIngredientPurchase,
)
from apps.food_ingredients.food_ingredient.services import convert
from apps.stories.electric_power_x_store.models import ElectricPower_x_Store
from apps.stories.average_hourly_wage_x_store.models import (
    AverageHourlyWage_x_Store,
)
from apps.units.unit.models import Unit
from apps.units.unit.services import convert_same_quantity

from .models import BaseRecipe


# ---------------------------------------------------------------------------
# Cache simples da unidade kW (evita query repetida dentro do mesmo cálculo)
# ---------------------------------------------------------------------------
_KW_CACHE = {"unit": None, "loaded": False}


def _get_kw_unit():
    """Devolve a Unit 'kW' (ou None se não existir)."""
    if not _KW_CACHE["loaded"]:
        _KW_CACHE["unit"] = Unit.objects.filter(symbol="kW").first()
        _KW_CACHE["loaded"] = True
    return _KW_CACHE["unit"]


def _potencia_em_kw(machinery) -> Decimal:
    """
    Converte a potência do maquinário para kW.

    O campo `qtde_power` está na unidade `unit_power`. A tarifa é em R$/kWh,
    então precisamos converter para kW. Usa a benchmark da grandeza
    (potência → W) como ponte.
    """
    if not machinery or not machinery.qtde_power:
        return Decimal("0")

    kw = _get_kw_unit()
    if kw is None:
        # Sem unidade kW cadastrada: assume que qtde_power já está em kW
        return machinery.qtde_power

    return convert_same_quantity(
        quantity=machinery.qtde_power,
        from_unit=machinery.unit_power,
        to_unit=kw,
    )


# ---------------------------------------------------------------------------
# Buscas auxiliares
# ---------------------------------------------------------------------------
def _ultima_compra(food_ingredient):
    return (
        FoodIngredientPurchase.objects
        .filter(food_ingredient=food_ingredient)
        .select_related("unit")
        .order_by("-date", "-created_at")
        .first()
    )


def _tarifa_energia(store, ref_date: date):
    return (
        ElectricPower_x_Store.objects
        .filter(store=store, date__lte=ref_date)
        .order_by("-date")
        .first()
    )


def _salario_hora(store, ref_date: date):
    return (
        AverageHourlyWage_x_Store.objects
        .filter(store=store, date__lte=ref_date)
        .order_by("-date")
        .first()
    )


def _horas(execution_time) -> Decimal:
    """DurationField → horas (Decimal)."""
    if execution_time is None:
        return Decimal("0")
    segundos = execution_time.total_seconds()
    return Decimal(segundos) / Decimal("3600")


def _store_da_receita(receita):
    """
    Deriva a loja a partir do primeiro maquinário encontrado nas execuções.
    Se a BaseRecipe tiver FK para Store no futuro, troque por receita.store.
    """
    for ex in receita.execucoes.select_related("machinery__store"):
        if ex.machinery and ex.machinery.store_id:
            return ex.machinery.store
    return None


# ---------------------------------------------------------------------------
# Cálculo principal
# ---------------------------------------------------------------------------
def calcular_custo_receita(
    receita: BaseRecipe,
    data_referencia: date | None = None,
    incluir_energia: bool = True,
    incluir_mao_de_obra: bool = True,
) -> dict:
    data_ref = data_referencia or date.today()
    store = _store_da_receita(receita)

    tarifa = (
        _tarifa_energia(store, data_ref)
        if store and incluir_energia else None
    )
    salario = (
        _salario_hora(store, data_ref)
        if store and incluir_mao_de_obra else None
    )

    passos = []
    total_insumos = Decimal("0")
    total_energia = Decimal("0")
    total_mao_obra = Decimal("0")
    tempo_total_h = Decimal("0")

    execucoes = (
        receita.execucoes
        .select_related(
            "food_ingredient",
            "unidade_qtde_food_ingredient",
            "machinery__unit_power",
            "stage_execution",
            "operation_execution",
        )
        .order_by("elapsed_time")
    )

    for ex in execucoes:
        horas = _horas(ex.execution_time)
        tempo_total_h += horas

        # ---------- insumo ----------
        custo_insumo = Decimal("0")
        detalhe_insumo = None
        if (
            ex.food_ingredient
            and ex.qtde_food_ingredient
            and ex.unidade_qtde_food_ingredient
        ):
            compra = _ultima_compra(ex.food_ingredient)
            if compra:
                try:
                    qtde_na_unidade_da_compra = convert(
                        quantity=ex.qtde_food_ingredient,
                        from_unit=ex.unidade_qtde_food_ingredient,
                        to_unit=compra.unit,
                        food_ingredient=ex.food_ingredient,
                    )
                    custo_insumo = (
                        qtde_na_unidade_da_compra * compra.unit_price
                    )
                    detalhe_insumo = {
                        "food_ingredient": (
                            ex.food_ingredient.food_ingredient
                        ),
                        "qtde_receita": str(ex.qtde_food_ingredient),
                        "unidade_receita": (
                            ex.unidade_qtde_food_ingredient.symbol
                        ),
                        "qtde_convertida": str(qtde_na_unidade_da_compra),
                        "unidade_compra": compra.unit.symbol,
                        "unit_price": str(compra.unit_price),
                        "custo": str(custo_insumo),
                        "data_compra": compra.date.isoformat(),
                    }
                except Exception as e:
                    detalhe_insumo = {
                        "food_ingredient": (
                            ex.food_ingredient.food_ingredient
                        ),
                        "erro": f"conversão falhou: {e}",
                    }
            else:
                detalhe_insumo = {
                    "food_ingredient": ex.food_ingredient.food_ingredient,
                    "erro": "sem compra registrada",
                }

        # ---------- energia ----------
        custo_energia = Decimal("0")
        potencia_kw = _potencia_em_kw(ex.machinery)
        if tarifa and potencia_kw > 0:
            custo_energia = potencia_kw * horas * tarifa.fare_amount_kwh

        # ---------- mão de obra ----------
        custo_mao_obra = Decimal("0")
        if salario:
            custo_mao_obra = horas * salario.average_hourly_wage

        total_insumos += custo_insumo
        total_energia += custo_energia
        total_mao_obra += custo_mao_obra

        passos.append({
            "etapa": str(ex.stage_execution),
            "operacao": str(ex.operation_execution),
            "descricao": ex.description_execution,
            "tempo_h": str(horas),
            "maquinario": str(ex.machinery) if ex.machinery else None,
            "potencia_kw": str(potencia_kw),
            "insumo": detalhe_insumo,
            "custo_insumo": str(custo_insumo),
            "custo_energia": str(custo_energia),
            "custo_mao_obra": str(custo_mao_obra),
        })

    custo_total = total_insumos + total_energia + total_mao_obra

    return {
        "base_recipe": receita.base_recipe,
        "base_recipe_id": receita.id,
        "size": str(receita.size),
        "unit_size": receita.unit_size.symbol,
        "data_referencia": data_ref.isoformat(),
        "tarifa_energia": str(tarifa.fare_amount_kwh) if tarifa else None,
        "salario_hora": (
            str(salario.average_hourly_wage) if salario else None
        ),
        "tempo_total_h": str(tempo_total_h),
        "total_insumos": str(total_insumos),
        "total_energia": str(total_energia),
        "total_mao_obra": str(total_mao_obra),
        "custo_total": str(custo_total),
        "passos": passos,
    }
    
def calcular_balanco_massa(receita, data_referencia=None) -> dict:
    """
    Calcula o balanço de massa de uma receita.

    Pra cada insumo da receita:
      - converte a quantidade pra gramas (via densidade/porção)
      - aplica incorporation_percentage
      - soma

    Compara com o size da receita.
    """
    from apps.food_ingredients.food_ingredient.services import convert
    from apps.units.unit.services import convert_same_quantity

    # Unidade de massa benchmark (g)
    g_unit = Unit.objects.filter(
        physical_quantity__slug="massa", is_benchmark=True,
    ).first()
    if g_unit is None:
        return {"erro": "Unidade benchmark de massa (g) não encontrada."}

    itens = []
    erros = []
    peso_input = Decimal("0")

    for ex in receita.execucoes.select_related(
        "food_ingredient", "unidade_qtde_food_ingredient",
    ):
        if not (ex.food_ingredient and ex.qtde_food_ingredient
                and ex.unidade_qtde_food_ingredient):
            continue

        try:
            qtde_em_g = convert(
                quantity=ex.qtde_food_ingredient,
                from_unit=ex.unidade_qtde_food_ingredient,
                to_unit=g_unit,
                food_ingredient=ex.food_ingredient,
            )
        except Exception as e:
            erros.append(
                f"{ex.food_ingredient}: {e}"
            )
            continue

        pct = (ex.incorporation_percentage or Decimal("100")) / Decimal("100")
        peso_efetivo = qtde_em_g * pct
        peso_input += peso_efetivo

        itens.append({
            "insumo": ex.food_ingredient.food_ingredient,
            "qtde_original": f"{ex.qtde_food_ingredient} {ex.unidade_qtde_food_ingredient.symbol}",
            "qtde_em_g": str(qtde_em_g),
            "incorporation_percentage": str(ex.incorporation_percentage),
            "peso_efetivo_g": str(peso_efetivo),
        })

    # Converte o size pra gramas também
    try:
        size_em_g = convert_same_quantity(
            receita.size, receita.unit_size, g_unit,
        )
    except Exception:
        size_em_g = receita.size

    diferenca = peso_input - size_em_g
    diferenca_pct = (
        (diferenca / peso_input * Decimal("100"))
        if peso_input > 0 else Decimal("0")
    )

    # Classificação
    if peso_input < size_em_g:
        classificacao = "erro"  # input < output: impossível
    elif diferenca_pct >= Decimal("-5"):
        classificacao = "ok"
    elif diferenca_pct >= Decimal("-15"):
        classificacao = "atencao"
    else:
        classificacao = "suspeito"

    return {
        "receita": receita.base_recipe,
        "receita_id": receita.id,
        "size": str(receita.size),
        "unit_size": receita.unit_size.symbol,
        "size_em_g": str(size_em_g),
        "peso_input_g": str(peso_input),
        "diferenca_g": str(diferenca),
        "diferenca_pct": str(diferenca_pct),
        "classificacao": classificacao,
        "itens": itens,
        "erros": erros,
    }