# apps/products/product/tech_sheet.py
"""
Geração de ficha técnica em PDF para um produto.

O PDF é salvo em MEDIA_ROOT/tech_sheets/ com nome versionado:
    pao_de_queijo_v1.pdf
    pao_de_queijo_v2.pdf

Cada geração cria uma nova versão. A versão é incrementada automaticamente
com base nos arquivos já existentes na pasta.
"""

import re
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .cost import calcular_custo_produto
from .models import Product


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _slug(texto: str) -> str:
    """Converte 'Pão de Queijo' → 'pao_de_queijo'."""
    texto = texto.lower()
    substituicoes = {
        "á": "a", "à": "a", "ã": "a", "â": "a",
        "é": "e", "ê": "e",
        "í": "i",
        "ó": "o", "õ": "o", "ô": "o",
        "ú": "u",
        "ç": "c",
    }
    for orig, dest in substituicoes.items():
        texto = texto.replace(orig, dest)
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")


def _fmt(valor, casas=2) -> str:
    if valor is None:
        return "—"
    d = Decimal(str(valor))
    s = f"{d:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _proxima_versao(produto: Product) -> int:
    """Descobre a próxima versão livre olhando os arquivos existentes."""
    pasta = Path(settings.MEDIA_ROOT) / "tech_sheets"
    pasta.mkdir(parents=True, exist_ok=True)
    slug = _slug(produto.product)
    existentes = list(pasta.glob(f"{slug}_v*.pdf"))
    if not existentes:
        return 1
    versoes = []
    for f in existentes:
        m = re.search(r"_v(\d+)\.pdf$", f.name)
        if m:
            versoes.append(int(m.group(1)))
    return max(versoes) + 1 if versoes else 1


def _caminho_pdf(produto: Product, versao: int) -> Path:
    pasta = Path(settings.MEDIA_ROOT) / "tech_sheets"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta / f"{_slug(produto.product)}_v{versao}.pdf"


# ---------------------------------------------------------------------------
# Coleta de dados auxiliares
# ---------------------------------------------------------------------------
def _coletar_passos(produto: Product) -> list[dict]:
    """Coleta os passos (etapa/operação/tempo) dos sub-produtos do produto."""
    from apps.recipe.execution_operation_base_recipe.models import (
        ExecutionOperationBaseRecipe,
    )
    from apps.products.product_x_sub_product.models import (
        Product_x_Sub_Product,
    )

    passos = []
    links = (
        Product_x_Sub_Product.objects
        .filter(product=produto, active=True)
        .select_related("sub_product", "sub_product__base_recipe")
    )
    for link in links:
        receita = link.sub_product.base_recipe
        execs = (
            ExecutionOperationBaseRecipe.objects
            .filter(base_recipe=receita)
            .select_related("stage_execution", "operation_execution")
            .order_by("elapsed_time")
        )
        for ex in execs:
            seg = ex.execution_time.total_seconds() if ex.execution_time else 0
            horas = Decimal(str(seg)) / Decimal("3600")
            passos.append({
                "etapa": str(ex.stage_execution),
                "operacao": str(ex.operation_execution),
                "descricao": ex.description_execution,
                "tempo_h": str(horas),
            })
    return passos


def _coletar_ingredientes_por_subproduto(produto: Product) -> dict:
    """
    Para cada sub-produto do produto, devolve a lista de insumos
    da receita base, com quantidade, unidade e custo.

    Retorna:
        {
            sub_product_id: [
                {"insumo": "Polvilho", "qtde": "1.000", "unidade": "kg",
                 "custo": "R$ 6,30"},
                ...
            ],
            ...
        }
    """
    from apps.products.product_x_sub_product.models import (
        Product_x_Sub_Product,
    )
    from apps.recipe.execution_operation_base_recipe.models import (
        ExecutionOperationBaseRecipe,
    )
    from apps.food_ingredients.food_ingredient_purchase.models import (
        FoodIngredientPurchase,
    )
    from apps.food_ingredients.food_ingredient.services import convert

    resultado = {}

    links = (
        Product_x_Sub_Product.objects
        .filter(product=produto, active=True)
        .select_related("sub_product", "sub_product__base_recipe")
    )

    for link in links:
        receita = link.sub_product.base_recipe
        sub_id = link.sub_product.id

        execucoes = (
            ExecutionOperationBaseRecipe.objects
            .filter(base_recipe=receita, food_ingredient__isnull=False)
            .select_related(
                "food_ingredient",
                "unidade_qtde_food_ingredient",
            )
            .order_by("elapsed_time")
        )

        itens = []
        for ex in execucoes:
            insumo = ex.food_ingredient
            qtde = ex.qtde_food_ingredient
            unidade = ex.unidade_qtde_food_ingredient

            compra = (
                FoodIngredientPurchase.objects
                .filter(food_ingredient=insumo)
                .select_related("unit")
                .order_by("-date", "-created_at")
                .first()
            )

            custo_str = "—"
            if compra and qtde and unidade:
                try:
                    qtde_na_unidade_compra = convert(
                        quantity=qtde,
                        from_unit=unidade,
                        to_unit=compra.unit,
                        food_ingredient=insumo,
                    )
                    custo = qtde_na_unidade_compra * compra.unit_price
                    custo_str = f"R$ {_fmt(custo)}"
                except Exception:
                    custo_str = "—"

            peso_g = None
            if qtde and unidade:
                try:
                    from apps.units.unit.models import Unit
                    from apps.food_ingredients.food_ingredient.services import convert as conv
                    g_unit = Unit.objects.filter(
                        physical_quantity__slug="massa", is_benchmark=True,
                    ).first()
                    if g_unit:
                        peso_g = conv(
                            quantity=qtde,
                            from_unit=unidade,
                            to_unit=g_unit,
                            food_ingredient=insumo,
                        )
                except Exception:
                    peso_g = None
            

            itens.append({
                "insumo": insumo.food_ingredient,
                "qtde": _fmt(qtde, 3) if qtde else "—",
                "unidade": unidade.symbol if unidade else "—",
                "peso_g": _fmt(peso_g, 2) if peso_g else "—",                 # ← NOVO
                "incorporation_percentage": _fmt(ex.incorporation_percentage, 2),  # ← NOVO
                "custo": custo_str,
            })

        resultado[sub_id] = itens

    return resultado


# ---------------------------------------------------------------------------
# Construção do PDF
# ---------------------------------------------------------------------------
def _build_pdf(caminho: Path, produto: Product, custo: dict, versao: int):
    doc = SimpleDocTemplate(
        str(caminho),
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=f"Ficha Técnica — {produto.product}",
    )

    styles = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "Titulo", parent=styles["Title"], fontSize=16, spaceAfter=6,
    )
    subtitulo = ParagraphStyle(
        "Sub", parent=styles["Heading2"], fontSize=11, spaceBefore=8,
        spaceAfter=4, textColor=colors.HexColor("#333333"),
    )
    normal = styles["Normal"]

    elementos = []

    # ---- Cabeçalho ----
    elementos.append(Paragraph(
        f"FICHA TÉCNICA — {produto.product.upper()}", titulo,
    ))
    elementos.append(Paragraph(
        f"<b>Estabelecimento:</b> {produto.store}<br/>"
        f"<b>Categoria:</b> {produto.sub_category}<br/>"
        f"<b>Peso:</b> {_fmt(custo['weight'], 2)} {custo['unit']}<br/>"
        f"<b>Data:</b> {custo['data_referencia']}<br/>"
        f"<b>Versão:</b> v{versao}",
        normal,
    ))
    elementos.append(Spacer(1, 0.4 * cm))

    # ---- Composição (com ingredientes por sub-produto) ----
    elementos.append(Paragraph("Composição", subtitulo))

    ingredientes_por_sub = _coletar_ingredientes_por_subproduto(produto)

    for s in custo["sub_products"]:
        elementos.append(Paragraph(
            f"<b>▸ {s['sub_product']}</b> "
            f"({_fmt(s['composition_percentage'], 2)}%, "
            f"{_fmt(s['quantity_in_product'], 2)} {s['unit_in_product']})",
            normal,
        ))
        elementos.append(Paragraph(
            f"<i>Receita: {s['base_recipe']} "
            f"(rende {_fmt(s['recipe_size'], 2)} {s['recipe_unit']})</i>",
            normal,
        ))
        elementos.append(Spacer(1, 0.2 * cm))

        itens = ingredientes_por_sub.get(s["sub_product_id"], [])
        
        if itens:
            dados = [["Insumo", "Qtde", "Peso", "Incorp.", "Custo"]]
            for it in itens:
                dados.append([
                    it["insumo"],
                    f'{it["qtde"]} {it["unidade"]}',
                    it.get("peso_g", "—") + " g",
                    it.get("incorporation_percentage", "100.00") + "%",
                    it["custo"],
                ])
                
            t = Table(dados, colWidths=[6 * cm, 3 * cm, 2.5 * cm, 2 * cm, 3.5 * cm])
            
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEEEEE")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#BBBBBB")),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]))
            elementos.append(t)
        else:
            elementos.append(Paragraph(
                "<i>Nenhum ingrediente cadastrado nesta receita.</i>",
                normal,
            ))

        elementos.append(Spacer(1, 0.4 * cm))

    # ---- Modo de preparo ----
    elementos.append(Paragraph("Modo de preparo", subtitulo))
    dados_prep = [["Etapa", "Operação", "Descrição", "Tempo"]]
    for p in custo.get("passos", []):
        dados_prep.append([
            p["etapa"],
            p["operacao"],
            p["descricao"],
            f'{_fmt(p["tempo_h"], 3)} h',
        ])
    if len(dados_prep) > 1:
        t = Table(dados_prep, colWidths=[3 * cm, 3 * cm, 8 * cm, 3 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDDDDD")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#999999")),
        ]))
        elementos.append(t)
    else:
        elementos.append(Paragraph(
            "<i>Modo de preparo não disponível.</i>", normal,
        ))
    elementos.append(Spacer(1, 0.4 * cm))

    # ---- Custo ----
    elementos.append(Paragraph("Custo", subtitulo))
    dados_custo = [
        ["Componente", "Valor"],
        ["Custo do produto", f"R$ {_fmt(custo['custo_produto'])}"],
        ["Markup", f"{_fmt(custo['markup_default'], 2)} %"],
        ["Preço bruto", f"R$ {_fmt(custo['preco_bruto'])}"],
    ]
    t = Table(dados_custo, colWidths=[10 * cm, 7 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDDDDD")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#999999")),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
    ]))
    elementos.append(t)
    elementos.append(Spacer(1, 0.3 * cm))

    # ---- Preço final ----
    preco_style = ParagraphStyle(
        "Preco", parent=styles["Heading1"], fontSize=18,
        textColor=colors.HexColor("#0B6E4F"), alignment=1,
    )
    elementos.append(Paragraph(
        f"PREÇO DE VENDA: R$ {_fmt(custo['preco_sugerido'])}",
        preco_style,
    ))

    doc.build(elementos)


# ---------------------------------------------------------------------------
# API principal
# ---------------------------------------------------------------------------
def gerar_ficha_tecnica(produto: Product, data_referencia=None) -> dict:
    """
    Gera o PDF da ficha técnica do produto.

    Cria um arquivo versionado em MEDIA_ROOT/tech_sheets/.
    Devolve metadados: caminho, versão, url relativa.
    """
    custo = calcular_custo_produto(produto, data_referencia=data_referencia)
    custo["passos"] = _coletar_passos(produto)

    versao = _proxima_versao(produto)
    caminho = _caminho_pdf(produto, versao)
    _build_pdf(caminho, produto, custo, versao)

    relativo = caminho.relative_to(Path(settings.MEDIA_ROOT))
    url = f"{settings.MEDIA_URL}{relativo.as_posix()}"

    return {
        "product_id": produto.id,
        "product": produto.product,
        "version": versao,
        "file": str(caminho),
        "url": url,
        "filename": caminho.name,
    }