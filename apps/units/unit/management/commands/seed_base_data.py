from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.recipe.operation_base_recipe.models import OperationBaseRecipe
from apps.recipe.stage_base_recipe.models import StageBaseRecipe
from apps.stories.store.models import Store
from apps.units.physical_quantity.models import PhysicalQuantity
from apps.units.unit.models import Unit


PHYSICAL_QUANTITIES = [
    ("massa", "massa"),
    ("volume", "volume"),
    ("temperatura", "temperatura"),
    ("comprimento", "comprimento"),
    ("área", "área"),
    ("unidade", "unidade"),
    ("tarifa energia", "tarifa-energia"),
    ("salário por hora", "salario-por-hora"),
    ("potência", "potencia"),
]


UNITS = [
    # (unidade, símbolo, slug da grandeza, é_benchmark, fator de conversão)
    ("miligrama", "mg", "massa", False, "0.001"),
    ("grama", "gr", "massa", True, "1"),
    ("kilograma", "kg", "massa", False, "1000"),

    ("mililitro", "ml", "volume", True, "1"),
    ("litro", "l", "volume", False, "1000"),
    ("cm cúbico", "cm3", "volume", False, "1"),

    ("unidade", "un", "unidade", True, "1"),
    ("dúzia", "dz", "unidade", False, "12"),
    ("cento", "ct", "unidade", False, "100"),

    ("grau celsius", "°C", "temperatura", True, "1"),

    ("metro", "m", "comprimento", True, "1"),
    ("centímetro", "cm", "comprimento", False, "0.01"),

    ("metro quadrado", "m2", "área", True, "1"),

    ("tarifa energia elétrica", "kwh", "tarifa-energia", True, "1"),
    ("salário por hora", "sph", "salario-por-hora", True, "1"),
    ("watt", "W", "potencia", True, "1"),
    ("kilowatt", "kW", "potencia", False, "1000"),    
]


STAGES = [
    "homogeneização",
    "cozimento",
    "fermentação",
    "maturação",
    "resfriamento",
    "aquecimento",
    "correção do pH",
    "separação",
]


OPERATIONS = [
    "sovar",
    "misturar",
    "assar",
    "resfriar",
    "fermentar",
    "maturar",
    "mexer",
    "inserir",
    "retirar",
]


class Command(BaseCommand):
    help = (
        "Popula grandezas físicas, unidades, a loja inicial, "
        "etapas e operações da receita base."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        # ---------------------------------------------------------------
        # Grandezas físicas
        # ---------------------------------------------------------------
        self.stdout.write("Populando grandezas físicas...")
        for nome, slug in PHYSICAL_QUANTITIES:
            pq, created = PhysicalQuantity.objects.update_or_create(
                slug=slug,
                defaults={"physical_quantity": nome},
            )
            self.stdout.write(f"  {'+' if created else '='} {pq.slug}")

        # ---------------------------------------------------------------
        # Unidades
        # ---------------------------------------------------------------
        self.stdout.write("Populando unidades...")
        for nome, simbolo, pq_slug, is_benchmark, factor in UNITS:
            pq = PhysicalQuantity.objects.get(slug=pq_slug)
            unit, created = Unit.objects.update_or_create(
                unit=nome,
                physical_quantity=pq,
                defaults={
                    "symbol": simbolo,
                    "is_benchmark": is_benchmark,
                    "conversion_factor": Decimal(factor),
                },
            )
            self.stdout.write(f"  {'+' if created else '='} {unit.unit} ({unit.symbol})")

        # ---------------------------------------------------------------
        # Loja inicial
        # ---------------------------------------------------------------
        self.stdout.write("Populando loja inicial...")
        store, created = Store.objects.update_or_create(
            id_store=1,
            defaults={"name_store": "Lanchonete da Vê"},
        )
        self.stdout.write(f"  {'+' if created else '='} {store.name_store}")

        # ---------------------------------------------------------------
        # Etapas da receita base
        # ---------------------------------------------------------------
        self.stdout.write("Populando etapas da receita base...")
        for nome in STAGES:
            obj, created = StageBaseRecipe.objects.update_or_create(
                stage_base_recipe=nome,
            )
            self.stdout.write(f"  {'+' if created else '='} {obj.stage_base_recipe}")

        # ---------------------------------------------------------------
        # Operações da receita base
        # ---------------------------------------------------------------
        self.stdout.write("Populando operações da receita base...")
        for nome in OPERATIONS:
            obj, created = OperationBaseRecipe.objects.update_or_create(
                operation_base_recipe=nome,
            )
            self.stdout.write(f"  {'+' if created else '='} {obj.operation_base_recipe}")

        self.stdout.write(self.style.SUCCESS("Dados base populados."))