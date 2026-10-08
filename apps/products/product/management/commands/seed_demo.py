"""
ATENÇÃO: dados de DEMONSTRAÇÃO. Não usar em produção.

Popula o cenário mínimo do pão de queijo:
  - 3 insumos (farinha, queijo, ovo) + compras + porção do ovo
  - 3 utensílios + 1 maquinário
  - 1 receita base com 3 passos de execução (com utensílios e maquinário)
  - 1 subproduto
  - 1 produto + composição
"""

from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.food_ingredients.food_ingredient.models import FoodIngredient
from apps.food_ingredients.food_ingredient_portion.models import FoodIngredientPortion
from apps.food_ingredients.food_ingredient_purchase.models import FoodIngredientPurchase
from apps.food_ingredients.supplier_food_ingredients.models import SupplierFoodIngredients
from apps.machinerys.machinery.models import Machinery, Utensil
from apps.products.product.models import Product
from apps.products.product_x_sub_product.models import Product_x_Sub_Product
from apps.products_div.product_sub_category.models import ProductSubCategory
from apps.products_div.sub_product_sub_type.models import SubProductSubType
from apps.recipe.base_recipe.models import BaseRecipe
from apps.recipe.execution_operation_base_recipe.models import ExecutionOperationBaseRecipe
from apps.recipe.operation_base_recipe.models import OperationBaseRecipe
from apps.recipe.stage_base_recipe.models import StageBaseRecipe
from apps.stories.store.models import Store
from apps.sub_products.sub_product.models import SubProduct
from apps.units.unit.models import Unit


class Command(BaseCommand):
    help = "Popula o cenário de demonstração do pão de queijo. Idempotente."

    @transaction.atomic
    def handle(self, *args, **options):
        # ------------------------------------------------------------------
        # Lookups
        # ------------------------------------------------------------------
        grama = Unit.objects.get(unit="grama")
        kilograma = Unit.objects.get(unit="kilograma")
        unidade = Unit.objects.get(unit="unidade")
        watt = Unit.objects.get(unit="watt") if Unit.objects.filter(unit="watt").exists() else None
        fornecedor = SupplierFoodIngredients.objects.get(supplier="Assaí")
        loja = Store.objects.get(id_store=1)
        etapa = StageBaseRecipe.objects.get(stage_base_recipe="homogeneização")
        operacao = OperationBaseRecipe.objects.get(operation_base_recipe="misturar")
        sub_categoria = ProductSubCategory.objects.get(sub_category="travesseirinhos grandes")
        sub_tipo = SubProductSubType.objects.get(sub_product_sub_type="massa de pão de queijo")

        # ------------------------------------------------------------------
        # Utensílios
        # ------------------------------------------------------------------
        self.stdout.write("Utensílios...")
        utensilios_def = [
            ("Assadeira grande", "ASS-G", "assadeira de metal 40×30 cm"),
            ("Assadeira média", "ASS-M", "assadeira de metal 30×20 cm"),
            ("Cuba de mistura 5 L", "CUB-1", "cuba inox para mistura de massas"),
            ("Tábua de corte branca", "TAB-1", "tábua de polietileno 40×30 cm"),
        ]
        utensilios = {}
        for nome, code, desc in utensilios_def:
            obj, created = Utensil.objects.update_or_create(
                code=code,
                defaults={
                    "utensil": nome,
                    "description": desc,
                    "store": loja,
                    "active": True,
                },
            )
            utensilios[code] = obj
            self.stdout.write(f"  {'+' if created else '='} {obj.code} — {obj.utensil}")

        # ------------------------------------------------------------------
        # Maquinário
        # ------------------------------------------------------------------
        self.stdout.write("Maquinário...")
        if watt is None:
            self.stdout.write(
                self.style.WARNING(
                    "  ! Unidade 'watt' não existe. Pulando maquinário. "
                    "Adicione 'watt' em Units e rode de novo."
                )
            )
            forno = None
        else:
            forno, created = Machinery.objects.update_or_create(
                code="FOR-01",
                defaults={
                    "machinery": "Forno elétrico 2 kW",
                    "description": "forno elétrico de bancada, 2 kW",
                    "qtde_power": Decimal("2000"),
                    "unit_power": watt,
                    "value_machinery": Decimal("800.00"),
                    "store": loja,
                    "active": True,
                },
            )
            self.stdout.write(f"  {'+' if created else '='} {forno.code} — {forno.machinery}")

        # ------------------------------------------------------------------
        # Insumos
        # ------------------------------------------------------------------
        self.stdout.write("Insumos...")
        insumos_def = [
            ("Farinha de Trigo", "farinha de trigo tipo 1", grama),
            ("Queijo Minas", "queijo minas padrão", grama),
            ("Ovo", "ovo de galinha", unidade),
        ]
        insumos = {}
        for nome, desc, unit in insumos_def:
            obj, created = FoodIngredient.objects.update_or_create(
                food_ingredient=nome,
                defaults={
                    "description": desc,
                    "qtde_default_shopping": Decimal("1") if unit == grama else Decimal("12"),
                    "unit": unit,
                    "supplier": fornecedor,
                    "active": True,
                },
            )
            insumos[nome] = obj
            self.stdout.write(f"  {'+' if created else '='} {obj.food_ingredient}")

        # ------------------------------------------------------------------
        # Porção do ovo (1 un = 55 g)
        # ------------------------------------------------------------------
        self.stdout.write("Porção do ovo...")
        FoodIngredientPortion.objects.update_or_create(
            food_ingredient=insumos["Ovo"],
            unit=unidade,
            date=date.today(),
            defaults={"reference_quantity": Decimal("55"), "reference_unit": grama},
        )

        # ------------------------------------------------------------------
        # Compras
        # ------------------------------------------------------------------
        self.stdout.write("Compras...")
        compras_def = [
            ("Farinha de Trigo", Decimal("1"), kilograma, Decimal("5.00")),
            ("Queijo Minas", Decimal("1"), kilograma, Decimal("40.00")),
            ("Ovo", Decimal("12"), unidade, Decimal("12.00")),
        ]
        for nome, qtde, unit, total in compras_def:
            FoodIngredientPurchase.objects.update_or_create(
                food_ingredient=insumos[nome],
                date=date.today(),
                defaults={"quantity": qtde, "unit": unit, "total_price": total},
            )
            self.stdout.write(f"  {qtde} {unit.symbol} de {nome} por R$ {total}")

        # ------------------------------------------------------------------
        # Receita base
        # ------------------------------------------------------------------
        self.stdout.write("Receita base...")
        receita, created = BaseRecipe.objects.update_or_create(
            base_recipe="massa de pão de queijo",
            defaults={
                "description": "massa básica de pão de queijo",
                "size": Decimal("1000"),
                "unit_size": grama,
                "active": True,
            },
        )
        self.stdout.write(f"  {'+' if created else '='} {receita.base_recipe}")

        # ------------------------------------------------------------------
        # Passos de execução (com utensílios e maquinário)
        # ------------------------------------------------------------------
        self.stdout.write("Passos de execução...")
        passos_def = [
            {
                "desc": "misturar farinha",
                "insumo": "Farinha de Trigo",
                "qtde": Decimal("500"),
                "unit": grama,
                "utensils": ["CUB-1", "TAB-1"],
                "machinery": None,
            },
            {
                "desc": "misturar queijo",
                "insumo": "Queijo Minas",
                "qtde": Decimal("200"),
                "unit": grama,
                "utensils": ["CUB-1"],
                "machinery": None,
            },
            {
                "desc": "misturar ovos",
                "insumo": "Ovo",
                "qtde": Decimal("2"),
                "unit": unidade,
                "utensils": ["CUB-1"],
                "machinery": None,
            },
            {
                "desc": "assar",
                "insumo": None,
                "qtde": None,
                "unit": None,
                "utensils": ["ASS-G"],
                "machinery": forno,
            },
        ]

        for p in passos_def:
            defaults = {
                "description_execution": p["desc"],
                "qtde_food_ingredient": p["qtde"],
                "unidade_qtde_food_ingredient": p["unit"],
                "incorporation_percentage": False,
                "elapsed_time": timedelta(minutes=5),
                "machinery": p["machinery"],
            }
            if p["insumo"]:
                defaults["food_ingredient"] = insumos[p["insumo"]]
            else:
                defaults["food_ingredient"] = None

            # update_or_create exige chave sem None. Usamos base+stage+operation+descrição
            # como chave natural composta via busca por atributos.
            existing = ExecutionOperationBaseRecipe.objects.filter(
                base_recipe=receita,
                stage_execution=etapa,
                operation_execution=operacao,
                description_execution=p["desc"],
            ).first()

            if existing:
                for k, v in defaults.items():
                    setattr(existing, k, v)
                existing.save()
                obj = existing
                created = False
            else:
                obj = ExecutionOperationBaseRecipe.objects.create(
                    base_recipe=receita,
                    stage_execution=etapa,
                    operation_execution=operacao,
                    **defaults,
                )
                created = True

            # M2M
            codes = [utensilios[c] for c in p["utensils"] if c in utensilios]
            obj.utensils.set(codes)

            self.stdout.write(
                f"  {'+' if created else '='} {p['desc']} "
                f"(utensílios: {', '.join(p['utensils']) or '—'}; "
                f"maquinário: {obj.machinery.code if obj.machinery else '—'})"
            )

        # ------------------------------------------------------------------
        # Subproduto
        # ------------------------------------------------------------------
        self.stdout.write("Subproduto...")
        sub, created = SubProduct.objects.update_or_create(
            sub_product="massa de pão de queijo cru",
            defaults={
                "base_recipe": receita,
                "sub_product_sub_type": sub_tipo,
                "active": True,
            },
        )
        self.stdout.write(f"  {'+' if created else '='} {sub.sub_product}")

        # ------------------------------------------------------------------
        # Produto
        # ------------------------------------------------------------------
        self.stdout.write("Produto...")
        produto, created = Product.objects.update_or_create(
            store=loja,
            product="Pão de Queijo",
            defaults={
                "description_product": "pão de queijo mineiro, feito na casa",
                "name_menu": "Pão de Queijo",
                "description_menu": "pão de queijo quentinho",
                "sub_category": sub_categoria,
                "active": True,
            },
        )
        self.stdout.write(f"  {'+' if created else '='} {produto.product}")

        # ------------------------------------------------------------------
        # Composição produto × subproduto
        # ------------------------------------------------------------------
        self.stdout.write("Composição...")
        Product_x_Sub_Product.objects.update_or_create(
            product=produto,
            sub_product=sub,
            defaults={"bakers_percentage": Decimal("100"), "active": True},
        )
        self.stdout.write("  produto × subproduto")

        self.stdout.write(self.style.SUCCESS("\nCenário de demonstração populado."))
        self.stdout.write(f"  Produto id: {produto.id}")
        self.stdout.write(
            f"  Teste: /api/products/{produto.id}/scale/?quantity=500&unit={grama.id}"
        )
        self.stdout.write(
            f"  Teste: /api/products/{produto.id}/cost/?quantity=500&unit={grama.id}"
        )