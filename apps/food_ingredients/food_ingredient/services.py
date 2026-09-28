"""
Conversão de quantidades envolvendo insumos.

- Mesma grandeza: usa os fatores de conversão das unidades.
- Massa <-> Volume: usa a densidade mais recente do insumo.
"""

from decimal import Decimal

from apps.units.unit.models import Unit
from apps.units.unit.services import (
    ConversionError,
    IncompatibleQuantitiesError,
    convert_same_quantity,
)
from apps.food_ingredients.food_ingredient_density.models import FoodIngredientDensity

from .models import FoodIngredient


class DensityNotFoundError(ConversionError):
    """Não há densidade cadastrada que permita a conversão massa <-> volume."""


_MASS_NAME = "massa"
_VOLUME_NAME = "volume"


def _pq_name(unit: Unit) -> str:
    return (unit.physical_quantity.slug or "").strip().lower()


def _pair_mass_volume(from_unit: Unit, to_unit: Unit) -> tuple[Unit, Unit] | None:
    """
    Se uma unidade for de Massa e a outra de Volume, retorna (mass_unit, volume_unit).
    Caso contrário, retorna None.
    """
    from_name = _pq_name(from_unit)
    to_name = _pq_name(to_unit)
    if from_name == _MASS_NAME and to_name == _VOLUME_NAME:
        return from_unit, to_unit
    if from_name == _VOLUME_NAME and to_name == _MASS_NAME:
        return to_unit, from_unit
    return None


def get_latest_density(
    food_ingredient: FoodIngredient,
    mass_unit: Unit,
    volume_unit: Unit,
) -> FoodIngredientDensity | None:
    """
    Densidade mais recente do insumo compatível com as grandezas das unidades dadas.
    """
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


def convert(
    quantity: Decimal,
    from_unit: Unit,
    to_unit: Unit,
    food_ingredient: FoodIngredient,
) -> Decimal:
    """
    Converte uma quantidade de from_unit para to_unit no contexto de um insumo.

    - Mesma grandeza: conversão direta via conversion_factor.
    - Massa <-> Volume: usa a densidade mais recente do insumo.

    Levanta IncompatibleQuantitiesError se as grandezas não permitirem conversão
    e DensityNotFoundError se faltar densidade cadastrada.
    """
    # Mesma grandeza: basta fator de conversão
    if from_unit.physical_quantity_id == to_unit.physical_quantity_id:
        return convert_same_quantity(quantity, from_unit, to_unit)

    # Massa <-> Volume: precisa de densidade
    pair = _pair_mass_volume(from_unit, to_unit)
    if pair is None:
        raise IncompatibleQuantitiesError(
            f"Não é possível converter {from_unit} em {to_unit}: "
            "grandezas incompatíveis e sem densidade aplicável."
        )
    mass_unit, volume_unit = pair

    density_row = get_latest_density(food_ingredient, mass_unit, volume_unit)
    if density_row is None:
        raise DensityNotFoundError(
            f"Nenhuma densidade cadastrada para '{food_ingredient}' "
            f"compatível com a conversão {from_unit} -> {to_unit}."
        )

    # Densidade expressa em (benchmark de massa) por (benchmark de volume).
    # Ex.: 1.03 kg/L  →  densidade_bm = 1.03 × 1000 / 1000 = 1.03 g/mL
    density_bm = (
        density_row.density
        * density_row.mass_unit.conversion_factor
        / density_row.volume_unit.conversion_factor
    )

    from_is_mass = from_unit.physical_quantity_id == mass_unit.physical_quantity_id

    if from_is_mass:
        # from_unit é massa, to_unit é volume
        mass_bm = quantity * from_unit.conversion_factor
        volume_bm = mass_bm / density_bm
        return volume_bm / to_unit.conversion_factor
    else:
        # from_unit é volume, to_unit é massa
        volume_bm = quantity * from_unit.conversion_factor
        mass_bm = volume_bm * density_bm
        return mass_bm / to_unit.conversion_factor