from django.core.management.base import BaseCommand
from django.db import transaction

from apps.products_div.product_category.models import ProductCategory
from apps.products_div.product_sub_category.models import ProductSubCategory
from apps.products_div.sub_product_type.models import SubProductType
from apps.products_div.sub_product_sub_type.models import SubProductSubType


CATEGORIES = [
    # (category, description_menu, active)
    ("Pratos Executivos", "refeições para o dia-a-dia", True),
    ("Salgados", "totalmente feitos na casa", True),
    ("Sobremesas", "Dê uma doçura na sua vida. Feitas na casa.", True),
]


SUB_CATEGORIES = [
    # (category_name, sub_category, description_menu, active)
    ("Sobremesas", "bolos de pote", "bolos de pote", True),
    ("Sobremesas", "mousses", "mousses deliciosos", True),
    ("Pratos Executivos", "prato da casa", "prato habitual da casa.", True),
    ("Pratos Executivos", "prato do dia", "cada dia um prato diferente.", True),
    ("Salgados", "travesseirinhos grandes", "com 500g", True),
    ("Salgados", "travesseirinhos padrão", "com 250g", True),
]


SUB_PRODUCT_TYPES = [
    # (sub_product_type, active)
    ("empratamento", True),
    ("finalização", True),
    ("massa", True),
    ("molho", True),
    ("recheio", True),
]


SUB_PRODUCT_SUB_TYPES = [
    # (type_name, sub_product_sub_type, active)
    ("recheio", "frango desfiado para o travesseirinho", True),
    ("massa", "massa de bolinho de carne", True),
    ("massa", "massa de travesseirinho", True),
    ("molho", "molho de tomates para pizza", True),
]


class Command(BaseCommand):
    help = "Popula categorias, subcategorias, tipos e subtipos de produtos."

    @transaction.atomic
    def handle(self, *args, **options):
        # ---------------------------------------------------------------
        # Categorias
        # ---------------------------------------------------------------
        self.stdout.write("Populando categorias de produto...")
        for nome, descricao, active in CATEGORIES:
            obj, created = ProductCategory.objects.update_or_create(
                category=nome,
                defaults={"description_menu": descricao, "active": active},
            )
            self.stdout.write(f"  {'+' if created else '='} {obj.category}")

        # ---------------------------------------------------------------
        # Subcategorias
        # ---------------------------------------------------------------
        self.stdout.write("Populando subcategorias de produto...")
        for cat_nome, sub_nome, descricao, active in SUB_CATEGORIES:
            categoria = ProductCategory.objects.get(category=cat_nome)
            obj, created = ProductSubCategory.objects.update_or_create(
                category=categoria,
                sub_category=sub_nome,
                defaults={"description_menu": descricao, "active": active},
            )
            self.stdout.write(f"  {'+' if created else '='} {cat_nome} > {obj.sub_category}")

        # ---------------------------------------------------------------
        # Tipos de subproduto
        # ---------------------------------------------------------------
        self.stdout.write("Populando tipos de subproduto...")
        for nome, active in SUB_PRODUCT_TYPES:
            obj, created = SubProductType.objects.update_or_create(
                sub_product_type=nome,
                defaults={"active": active},
            )
            self.stdout.write(f"  {'+' if created else '='} {obj.sub_product_type}")

        # ---------------------------------------------------------------
        # Subtipos de subproduto
        # ---------------------------------------------------------------
        self.stdout.write("Populando subtipos de subproduto...")
        for tipo_nome, sub_nome, active in SUB_PRODUCT_SUB_TYPES:
            tipo = SubProductType.objects.get(sub_product_type=tipo_nome)
            obj, created = SubProductSubType.objects.update_or_create(
                type=tipo,
                sub_product_sub_type=sub_nome,
                defaults={"active": active},
            )
            self.stdout.write(f"  {'+' if created else '='} {tipo_nome} > {obj.sub_product_sub_type}")

        self.stdout.write(self.style.SUCCESS("Dados de products_div populados."))