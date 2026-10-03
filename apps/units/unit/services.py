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


class UnitFactor:
    """
    Resolve o fator de conversão de uma unidade para a benchmark
    da sua grandeza física, validando que a benchmark existe e que
    o fator da própria unidade é coerente.

    Uso:
        fator = UnitFactor.factor_to_benchmark(unit)
        qtd_em_benchmark = quantidade * fator
    """

    @classmethod
    def benchmark_for(cls, unit: Unit) -> Unit:
        """
        Devolve a unidade benchmark da mesma grandeza da `unit`.

        Levanta ConversionError se a grandeza não tiver benchmark.
        """
        benchmark = (
            Unit.objects
            .filter(
                physical_quantity=unit.physical_quantity,
                is_benchmark=True,
            )
            .first()
        )
        if benchmark is None:
            raise ConversionError(
                f"A grandeza '{unit.physical_quantity}' não tem "
                "unidade benchmark cadastrada."
            )
        return benchmark

    @classmethod
    def factor_to_benchmark(cls, unit: Unit) -> Decimal:
        """
        Fator para converter 1 `<unit>` na benchmark da sua grandeza.

        Ex.: se benchmark de massa é grama, `kg` devolve 1000.
        A própria benchmark devolve 1.

        Levanta ConversionError se a benchmark não existir, ou se o
        conversion_factor da unidade for inválido (<= 0, ou diferente
        de 1 quando a unidade for a própria benchmark).
        """
        benchmark = cls.benchmark_for(unit)

        if unit.pk == benchmark.pk:
            if unit.conversion_factor != Decimal("1"):
                raise ConversionError(
                    f"A unidade benchmark '{unit}' tem "
                    f"conversion_factor={unit.conversion_factor}, "
                    "esperado 1."
                )
            return Decimal("1")

        if unit.conversion_factor <= 0:
            raise ConversionError(
                f"A unidade '{unit}' tem conversion_factor inválido: "
                f"{unit.conversion_factor}."
            )

        return unit.conversion_factor


def to_benchmark(quantity: Decimal, unit: Unit) -> Decimal:
    """Converte uma quantidade para a unidade referencial da grandeza."""
    return quantity * UnitFactor.factor_to_benchmark(unit)


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