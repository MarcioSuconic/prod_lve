# apps/productions/pending_production/services.py
"""
Serviço de planejamento de produção.

Dado um PendingProduction (com itens: produto + quantidade), calcula:
  1. Sub-produtos necessários (expandindo cada produto)
  2. Consolidação (soma sub-produtos iguais)
  3. Arredondamento não-proporcional (múltiplos inteiros)
  4. Cronograma
  5. Custo (insumos + energia + mão de obra)
  6. Lista de compras (consolidada)

Sem cascata: produtos ficam na quantidade original. Avisa sobre sobras.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_CEILING

from apps.food_ingredients.food_ingredient_purchase.models import (
    FoodIngredientPurchase,
)
from apps.food_ingredients.food_ingredient.services import convert
from apps.products.product_x_sub_product.models import (
    Product_x_Sub_Product,
)
from apps.recipe.base_recipe.models import BaseRecipe
from apps.recipe.base_recipe.services import calcular_custo_receita
from apps.recipe.execution_operation_base_recipe.models import (
    ExecutionOperationBaseRecipe,
)
from apps.units.unit.services import convert_same_quantity

from .models import PendingProduction


class ProductionPlanError(Exception):
    """Erro ao calcular plano de produção."""


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------
def _ceil(valor: Decimal) -> int:
    """Arredonda pra cima (inteiro)."""
    return int(valor.to_integral_value(rounding=ROUND_CEILING))


# ---------------------------------------------------------------------------
# 1. Expande produtos em sub-produtos
# ---------------------------------------------------------------------------
def _expandir_sub_produtos(items):
    """
    items = lista de ProductionXProduct (product, quantity, unit)

    Devolve lista de dicts:
        [
            {
                "sub_product_id": 1,
                "sub_product": "massa de pão de queijo",
                "base_recipe_id": 1,
                "base_recipe": "massa de pão de queijo",
                "quantity_pedida": Decimal("2900.000"),
                "unit": <Unit>,
                "origem": ["Pão de Queijo (50 un)"],
            },
            ...
        ]
    """
    resultado = []

    for item in items:
        product = item.product
        quantidade_produto = item.quantity
        unidade_produto = item.unit

        vinculos = (
            Product_x_Sub_Product.objects
            .filter(product=product, active=True)
            .select_related(
                "sub_product",
                "sub_product__base_recipe",
                "sub_product__base_recipe__unit_size",
            )
        )

        if not vinculos.exists():
            raise ProductionPlanError(
                f"Produto '{product}' não tem sub-produtos ativos."
            )

        peso_produto = product.product_weight_or_volume
        unidade_produto_peso = product.unit_weight_or_volume

        for v in vinculos:
            pct = v.composition_percentage / Decimal("100")
            qtd_no_produto = peso_produto * pct
            qtd_total = qtd_no_produto * quantidade_produto

            resultado.append({
                "sub_product_id": v.sub_product.id,
                "sub_product": str(v.sub_product),
                "base_recipe_id": v.sub_product.base_recipe.id,
                "base_recipe": str(v.sub_product.base_recipe),
                "quantity_pedida": qtd_total,
                "unit": unidade_produto_peso,
                "origem": [
                    f"{product} ({quantidade_produto} {unidade_produto.symbol})"
                ],
            })

    return resultado


# ---------------------------------------------------------------------------
# 2. Consolida sub-produtos iguais
# ---------------------------------------------------------------------------
def _consolidar(sub_produtos):
    """Agrupa por sub_product_id, somando as quantidades."""
    consolidado = {}

    for sp in sub_produtos:
        key = sp["sub_product_id"]
        if key not in consolidado:
            consolidado[key] = {
                **sp,
                "quantity_pedida": Decimal("0"),
                "origem": [],
            }
        consolidado[key]["quantity_pedida"] += sp["quantity_pedida"]
        consolidado[key]["origem"].extend(sp["origem"])

    return list(consolidado.values())


# ---------------------------------------------------------------------------
# 3. Arredondamento não-proporcional
# ---------------------------------------------------------------------------
def _arredondar(sub_produtos):
    """
    Para cada sub-produto:
      - Escala a receita base para a quantidade pedida
      - Verifica se tem insumo não-proporcional
      - Se sim, arredonda pra o próximo múltiplo inteiro
      - Recalcula o fator da receita
      - Devolve o fator final

    Devolve (sub_produtos_finais, avisos).
    """
    avisos = []
    finais = []

    for sp in sub_produtos:
        receita_id = sp["base_recipe_id"]
        qtd_pedida = sp["quantity_pedida"]

        receita = BaseRecipe.objects.get(id=receita_id)

        size_receita = receita.size
        if size_receita == 0:
            raise ProductionPlanError(
                f"Receita '{receita}' tem tamanho zero."
            )

        # Converte a quantidade pedida pra unidade da receita
        qtd_pedida_na_receita = convert_same_quantity(
            qtd_pedida, sp["unit"], receita.unit_size,
        )

        fator_global = qtd_pedida_na_receita / size_receita

        execs = (
            ExecutionOperationBaseRecipe.objects
            .filter(
                base_recipe=receita,
                food_ingredient__isnull=False,
            )
            .select_related("food_ingredient", "unidade_qtde_food_ingredient")
        )

        fator_final = fator_global
        motivos = []

        for ex in execs:
            insumo = ex.food_ingredient
            if not insumo:
                continue

            override = ex.not_proportional_override
            if override is None:
                not_prop = insumo.not_proportional
            else:
                not_prop = override

            if not not_prop:
                continue

            multiplo = insumo.qtde_default_shopping
            if not multiplo or multiplo <= 0:
                continue

            qtde_receita = ex.qtde_food_ingredient
            if not qtde_receita:
                continue

            qtde_pedida_insumo = qtde_receita * fator_global

            n = _ceil(qtde_pedida_insumo / multiplo)
            qtde_final = Decimal(n) * multiplo

            fator_insumo = (
                qtde_final / qtde_receita if qtde_receita else fator_global
            )

            if fator_insumo > fator_final:
                fator_final = fator_insumo

            sobra = qtde_final - qtde_pedida_insumo
            motivos.append(
                f"{insumo.food_ingredient}: {qtde_pedida_insumo:.2f} → "
                f"{qtde_final:.2f} ({n}×{multiplo}) — sobra {sobra:.2f}"
            )

        # Quantidade final do sub-produto
        qtd_final_receita = size_receita * fator_final
        qtd_final = convert_same_quantity(
            qtd_final_receita, receita.unit_size, sp["unit"],
        )

        ajustado = (qtd_final != qtd_pedida)

        if ajustado:
            avisos.append(
                f"Sub-produto '{sp['sub_product']}': "
                f"{qtd_pedida:.2f} → {qtd_final:.2f} {sp['unit'].symbol}. "
                + " | ".join(motivos)
            )

        finais.append({
            **sp,
            "quantity_pedida": qtd_pedida,
            "quantity_final": qtd_final,
            "fator": fator_final,
            "ajustado": ajustado,
            "motivos": motivos,
            "receita": receita,
        })

    return finais, avisos


# ---------------------------------------------------------------------------
# 4. Cronograma
# ---------------------------------------------------------------------------
def _calcular_cronograma(sub_produtos, data_inicio):
    """
    Calcula quando cada sub-produto começa/termina.

    Simplificação: assume que todos começam no início.
    TODO: usar o timing dos Product_x_Sub_Product.
    """
    cronograma = []
    for sp in sub_produtos:
        receita = sp["receita"]
        execs = receita.execucoes.all()
        if not execs.exists():
            continue

        max_seg = 0
        for ex in execs:
            el = ex.elapsed_time.total_seconds()
            et = ex.execution_time.total_seconds()
            if el + et > max_seg:
                max_seg = el + et

        duracao = timedelta(seconds=max_seg)
        cronograma.append({
            "sub_product": sp["sub_product"],
            "inicio": data_inicio.isoformat(),
            "fim": (data_inicio + duracao).isoformat(),
            "duracao_h": str(
                Decimal(str(duracao.total_seconds())) / Decimal("3600")
            ),
        })

    return cronograma


# ---------------------------------------------------------------------------
# 5. Custo
# ---------------------------------------------------------------------------
def _calcular_custo(sub_produtos, data_ref=None):
    """Custo total da produção (insumos + energia + mão de obra)."""
    data_ref = data_ref or date.today()

    total_insumos = Decimal("0")
    total_energia = Decimal("0")
    total_mao_obra = Decimal("0")

    detalhes = []
    for sp in sub_produtos:
        receita = sp["receita"]
        fator = sp["fator"]

        resultado = calcular_custo_receita(receita, data_referencia=data_ref)

        custo_insumo = Decimal(resultado["total_insumos"]) * fator
        custo_energia = Decimal(resultado["total_energia"]) * fator
        custo_mao_obra = Decimal(resultado["total_mao_obra"]) * fator

        total_insumos += custo_insumo
        total_energia += custo_energia
        total_mao_obra += custo_mao_obra

        detalhes.append({
            "sub_product": sp["sub_product"],
            "fator": str(fator),
            "custo_insumos": str(custo_insumo),
            "custo_energia": str(custo_energia),
            "custo_mao_obra": str(custo_mao_obra),
            "custo_total": str(
                custo_insumo + custo_energia + custo_mao_obra
            ),
        })

    return {
        "total": str(total_insumos + total_energia + total_mao_obra),
        "insumos": str(total_insumos),
        "energia": str(total_energia),
        "mao_de_obra": str(total_mao_obra),
        "detalhes": detalhes,
    }


# ---------------------------------------------------------------------------
# 6. Lista de compras
# ---------------------------------------------------------------------------
def _montar_lista_compras(sub_produtos, data_ref=None):
    """Consolida os insumos de todos os sub-produtos."""
    data_ref = data_ref or date.today()

    acumulado = {}

    for sp in sub_produtos:
        receita = sp["receita"]
        fator = sp["fator"]

        execs = (
            ExecutionOperationBaseRecipe.objects
            .filter(
                base_recipe=receita,
                food_ingredient__isnull=False,
            )
            .select_related(
                "food_ingredient",
                "unidade_qtde_food_ingredient",
            )
        )

        for ex in execs:
            insumo = ex.food_ingredient
            if not insumo or not ex.qtde_food_ingredient:
                continue

            qtde = ex.qtde_food_ingredient * fator
            unidade = ex.unidade_qtde_food_ingredient

            # Converte pra unidade padrão do insumo
            try:
                qtde_padrao = convert(
                    quantity=qtde,
                    from_unit=unidade,
                    to_unit=insumo.unit,
                    food_ingredient=insumo,
                )
            except Exception:
                qtde_padrao = qtde

            # Arredonda não-proporcional
            override = ex.not_proportional_override
            if override is None:
                not_prop = insumo.not_proportional
            else:
                not_prop = override

            if not_prop and insumo.qtde_default_shopping:
                multiplo = insumo.qtde_default_shopping
                n = _ceil(qtde_padrao / multiplo)
                qtde_padrao = Decimal(n) * multiplo

            # Custo — converte pra unidade da compra antes de multiplicar
            compra = (
                FoodIngredientPurchase.objects
                .filter(food_ingredient=insumo)
                .order_by("-date", "-created_at")
                .first()
            )
            custo = Decimal("0")
            if compra:
                try:
                    qtde_na_compra = convert(
                        quantity=qtde_padrao,
                        from_unit=insumo.unit,
                        to_unit=compra.unit,
                        food_ingredient=insumo,
                    )
                except Exception:
                    qtde_na_compra = qtde_padrao
                custo = qtde_na_compra * compra.unit_price

            key = insumo.id
            if key not in acumulado:
                acumulado[key] = {
                    "food_ingredient_id": insumo.id,
                    "food_ingredient": insumo.food_ingredient,
                    "quantity": Decimal("0"),
                    "unit_symbol": insumo.unit.symbol,
                    "not_proportional": not_prop,
                    "custo": Decimal("0"),
                }
            acumulado[key]["quantity"] += qtde_padrao
            acumulado[key]["custo"] += custo

    resultado = []
    for item in acumulado.values():
        resultado.append({
            "food_ingredient_id": item["food_ingredient_id"],
            "food_ingredient": item["food_ingredient"],
            "quantity": str(item["quantity"]),
            "unit": item["unit_symbol"],
            "not_proportional": item["not_proportional"],
            "custo": str(item["custo"]),
        })

    return sorted(resultado, key=lambda x: x["food_ingredient"])


# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------
def calcular_plano_producao(production_id: int) -> dict:
    """Calcula o plano completo de uma produção."""
    try:
        production = (
            PendingProduction.objects
            .select_related("store")
            .get(id=production_id)
        )
    except PendingProduction.DoesNotExist:
        raise ProductionPlanError(
            f"Produção {production_id} não encontrada."
        )

    items = list(production.items.filter(active=True))
    if not items:
        raise ProductionPlanError("A produção não tem itens ativos.")

    data_inicio = production.scheduled_start or datetime.now()

    expandido = _expandir_sub_produtos(items)
    consolidado = _consolidar(expandido)
    finais, avisos = _arredondar(consolidado)
    cronograma = _calcular_cronograma(finais, data_inicio)
    custo = _calcular_custo(finais)
    lista_compras = _montar_lista_compras(finais)

    data_fim = data_inicio
    for c in cronograma:
        fim = datetime.fromisoformat(c["fim"])
        if fim > data_fim:
            data_fim = fim

    return {
        "production_id": production.id,
        "store": str(production.store),
        "data_inicio": data_inicio.isoformat(),
        "data_fim": data_fim.isoformat(),
        "sub_produtos": [
            {
                "sub_product_id": sp["sub_product_id"],
                "sub_product": sp["sub_product"],
                "base_recipe": sp["base_recipe"],
                "quantity_pedida": str(sp["quantity_pedida"]),
                "quantity_final": str(sp["quantity_final"]),
                "unit": sp["unit"].symbol,
                "fator": str(sp["fator"]),
                "ajustado": sp["ajustado"],
                "motivos": sp["motivos"],
                "origem": sp["origem"],
            }
            for sp in finais
        ],
        "cronograma": cronograma,
        "custo": custo,
        "lista_compras": lista_compras,
        "avisos": avisos,
    }