"""
Agrupa apps no índice do Django Admin.

O Django agrupa por app_label. Como cada subpasta em apps/ é um app separado,
este módulo funde os apps listados em GROUP_MAP em grupos visuais.

Não altera app_label, não altera migrations, não altera db_table.
"""

from django.contrib.admin import AdminSite

# Mapeia app_label -> nome do grupo visual no admin
GROUP_MAP = {
    # Divisões de produto
    "product_category": "Divisões de Produto",
    "product_sub_category": "Divisões de Produto",
    "sub_product_type": "Divisões de Produto",
    "sub_product_sub_type": "Divisões de Produto",

    # Unidades
    "physical_quantity": "Unidades e Grandezas",
    "unit": "Unidades e Grandezas",

    # Histórico do estabelecimento
    "store": "Estabelecimento",
    "electric_power_x_store": "Estabelecimento",
    "average_hourly_wage_x_store": "Estabelecimento",

    # Insumos
    "food_ingredient": "Insumos",
    "supplier_food_ingredients": "Insumos",

    # Maquinário
    "machinery": "Maquinário",
    "machinery_scheduling": "Maquinário",

    # Receita
    "base_recipe": "Receita",
    "stage_base_recipe": "Receita",
    "process_base_recipe": "Receita",
    "execution_process_base_recipe": "Receita",

    # Produtos
    "product": "Produtos",
    "product_x_sub_product": "Produtos",
    "product_production": "Produtos",

    # Sub produtos
    "sub_product": "Sub Produtos",

    # Produção
    "register_production_sub_product": "Produção",
}


# Guarda a implementação original, ANTES de patchear
_original_get_app_list = AdminSite.get_app_list


def _grouped_get_app_list(self, request, app_label=None):
    app_list = _original_get_app_list(self, request, app_label)

    grouped = {}
    for app in app_list:
        label = app["app_label"]
        group_name = GROUP_MAP.get(label)

        if not group_name:
            # App não mapeado: mantém como está
            grouped[label] = app
            continue

        if group_name not in grouped:
            grouped[group_name] = {
                "name": group_name,
                "app_label": group_name,
                "app_url": app.get("app_url", ""),
                "has_module_perms": app.get("has_module_perms", True),
                "models": [],
            }
        grouped[group_name]["models"].extend(app["models"])

    # Ordena modelos dentro de cada grupo
    for group in grouped.values():
        group["models"].sort(key=lambda m: m["name"])

    return sorted(grouped.values(), key=lambda g: g["name"])


# Patch na CLASSE (não na instância). Pega em qualquer AdminSite, inclusive
# o admin.site padrão (que é um LazyObject).
AdminSite.get_app_list = _grouped_get_app_list