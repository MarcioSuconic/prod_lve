#/home/marcio/Desktop/projetos/app_prod_lve/apps/food_ingredients/food_ingredient/services.py
"""
Conversão de quantidades envolvendo insumos.

Três caminhos:
  1. Mesma grandeza               → fator de conversão (Unit.conversion_factor)
  2. Massa <-> Volume             → densidade (FoodIngredientDensity)
  3. Unidade de contagem <-> massa/volume → porção (FoodIngredientPortion)
"""

from decimal import Decimal

from apps.units.unit.models import Unit
from apps.units.unit.services import (
    ConversionError,
    IncompatibleQuantitiesError,
    convert_same_quantity,
)
from apps.food_ingredients.food_ingredient_density.models import FoodIngredientDensity
from apps.food_ingredients.food_ingredient_portion.models import FoodIngredientPortion

from .models import FoodIngredient


class DensityNotFoundError(ConversionError):
    """Não há densidade cadastrada que permita a conversão massa <-> volume."""


class PortionNotFoundError(ConversionError):
    """Não há porção cadastrada que permita a conversão contagem <-> massa/volume."""


_MASS_SLUG = "massa"
_VOLUME_SLUG = "volume"
_COUNT_SLUG = "unidade"


def _pq_slug(unit: Unit) -> str:
    return (unit.physical_quantity.slug or "").strip().lower()


def get_latest_density(
    food_ingredient: FoodIngredient,
    mass_unit: Unit,
    volume_unit: Unit,
) -> FoodIngredientDensity | None:
    return (
        FoodIngredientDensity.objects
        .filter(
            food_ingredient=food_ingredient,
            mass_unit__physical_quantity=mass_unit.physical_quantity,
            volume_unit__physical_quantity=volume_unit.physical_quantity,
        )
        .order_by("-date", "-created_at")
        .first()
    )


def get_latest_portion(
    food_ingredient: FoodIngredient,
    count_unit: Unit,
    reference_pq_slug: str,
) -> FoodIngredientPortion | None:
    """
    Porção mais recente do insumo com a unidade de contagem e a grandeza
    da unidade de referência dadas.
    """
    return (
        FoodIngredientPortion.objects
        .filter(
            food_ingredient=food_ingredient,
            unit=count_unit,
            reference_unit__physical_quantity__slug=reference_pq_slug,
        )
        .order_by("-date", "-created_at")
        .first()
    )


def _convert_via_density(
    quantity: Decimal,
    from_unit: Unit,
    to_unit: Unit,
    food_ingredient: FoodIngredient,
) -> Decimal:
    from_slug = _pq_slug(from_unit)
    to_slug = _pq_slug(to_unit)

    # Determina qual unidade é massa e qual é volume
    if from_slug == _MASS_SLUG and to_slug == _VOLUME_SLUG:
        mass_unit, volume_unit = from_unit, to_unit
        from_is_mass = True
    elif from_slug == _VOLUME_SLUG and to_slug == _MASS_SLUG:
        mass_unit, volume_unit = to_unit, from_unit
        from_is_mass = False
    else:
        raise IncompatibleQuantitiesError(
            f"Conversão {from_unit} -> {to_unit} não envolve massa e volume."
        )

    density_row = get_latest_density(food_ingredient, mass_unit, volume_unit)
    if density_row is None:
        raise DensityNotFoundError(
            f"Nenhuma densidade cadastrada para '{food_ingredient}' "
            f"compatível com {from_unit} -> {to_unit}."
        )

    density_bm = (
        density_row.density
        * density_row.mass_unit.conversion_factor
        / density_row.volume_unit.conversion_factor
    )

    if from_is_mass:
        mass_bm = quantity * from_unit.conversion_factor
        volume_bm = mass_bm / density_bm
        return volume_bm / to_unit.conversion_factor
    else:
        volume_bm = quantity * from_unit.conversion_factor
        mass_bm = volume_bm * density_bm
        return mass_bm / to_unit.conversion_factor


def _convert_via_portion(
    quantity: Decimal,
    from_unit: Unit,
    to_unit: Unit,
    food_ingredient: FoodIngredient,
) -> Decimal:
    from_slug = _pq_slug(from_unit)
    to_slug = _pq_slug(to_unit)

    if from_slug == _COUNT_SLUG and to_slug != _COUNT_SLUG:
        count_unit, other_unit, from_is_count = from_unit, to_unit, True
    elif to_slug == _COUNT_SLUG and from_slug != _COUNT_SLUG:
        count_unit, other_unit, from_is_count = to_unit, from_unit, False
    else:
        raise IncompatibleQuantitiesError(
            f"Conversão {from_unit} -> {to_unit} não envolve unidade de contagem."
        )

    # Procura porção registrada com count_unit OU com a benchmark da mesma
    # grandeza (ex.: porção em "unidade" também serve para converter "dúzia").
    # Procura porção registrada com count_unit OU com a benchmark da mesma
    # grandeza (ex.: porção em "unidade" também serve para converter "dúzia").
    benchmark_count_unit = (
        Unit.objects
        .filter(
            physical_quantity=count_unit.physical_quantity,
            is_benchmark=True,
        )
        .first()
    )
    if benchmark_count_unit is None:
        raise ConversionError(
            f"A grandeza '{count_unit.physical_quantity}' não tem "
            "unidade benchmark."
        )

    candidate_ids = {count_unit.id, benchmark_count_unit.id}

    portion = (
        FoodIngredientPortion.objects
        .filter(
            food_ingredient=food_ingredient,
            unit_id__in=candidate_ids,
            reference_unit__physical_quantity__slug=_pq_slug(other_unit),
        )
        .order_by("-date", "-created_at")
        .first()
    )
    if portion is None:
        raise PortionNotFoundError(
            f"Nenhuma porção cadastrada para '{food_ingredient}' "
            f"em {count_unit} ou {benchmark_count_unit} "
            f"com referência em {other_unit}."
        )

    if from_is_count:
        qty_in_portion_unit = convert_same_quantity(quantity, from_unit, portion.unit)
        qty_in_ref_unit = qty_in_portion_unit * portion.reference_quantity
        return convert_same_quantity(qty_in_ref_unit, portion.reference_unit, to_unit)
    else:
        qty_in_ref_unit = convert_same_quantity(quantity, from_unit, portion.reference_unit)
        qty_in_portion_unit = qty_in_ref_unit / portion.reference_quantity
        return convert_same_quantity(qty_in_portion_unit, portion.unit, to_unit)


def convert(
    quantity: Decimal,
    from_unit: Unit,
    to_unit: Unit,
    food_ingredient: FoodIngredient,
) -> Decimal:
    """
    Converte uma quantidade de from_unit para to_unit no contexto de um insumo.

    Tenta, em ordem:
      1. Mesma grandeza física.
      2. Massa <-> Volume via densidade.
      3. Contagem <-> massa/volume via porção.
    """
    from_slug = _pq_slug(from_unit)
    to_slug = _pq_slug(to_unit)

    # 1. Mesma grandeza
    if from_unit.physical_quantity_id == to_unit.physical_quantity_id:
        return convert_same_quantity(quantity, from_unit, to_unit)

    # 2. Massa <-> Volume
    if {from_slug, to_slug} == {_MASS_SLUG, _VOLUME_SLUG}:
        return _convert_via_density(quantity, from_unit, to_unit, food_ingredient)

    # 3. Contagem <-> massa/volume
    if _COUNT_SLUG in (from_slug, to_slug):
        return _convert_via_portion(quantity, from_unit, to_unit, food_ingredient)

    raise IncompatibleQuantitiesError(
        f"Não é possível converter {from_unit} em {to_unit}: "
        "grandezas incompatíveis e sem densidade ou porção aplicável."
    )