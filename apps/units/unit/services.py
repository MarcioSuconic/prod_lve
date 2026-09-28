"""
Conversão entre unidades da mesma grandeza física.

Toda conversão passa pela unidade referencial (benchmark) da grandeza:
    quantidade × from_unit.conversion_factor → benchmark
    benchmark / to_unit.conversion_factor → quantidade alvo
"""

from decimal import Decimal

from .models import Unit


class ConversionError(Exception):
    """Erro base para problemas de conversão de unidades."""


class IncompatibleQuantitiesError(ConversionError):
    """As unidades pertencem a grandezas físicas diferentes."""


def to_benchmark(quantity: Decimal, unit: Unit) -> Decimal:
    """Converte uma quantidade para a unidade referencial da grandeza."""
    return quantity * unit.conversion_factor


def from_benchmark(benchmark_quantity: Decimal, unit: Unit) -> Decimal:
    """Converte uma quantidade expressa em benchmark para a unidade dada."""
    return benchmark_quantity / unit.conversion_factor


def convert_same_quantity(quantity: Decimal, from_unit: Unit, to_unit: Unit) -> Decimal:
    """
    Converte entre duas unidades da mesma grandeza física.

    Levanta IncompatibleQuantitiesError se as grandezas forem diferentes.
    """
    if from_unit.physical_quantity_id != to_unit.physical_quantity_id:
        raise IncompatibleQuantitiesError(
            f"Não é possível converter {from_unit} em {to_unit}: "
            "grandezas físicas diferentes."
        )
    return from_benchmark(to_benchmark(quantity, from_unit), to_unit)