# apps/productions/pending_production/pdf.py
"""
Geração do PDF da lista de compras de uma produção planejada.

Sem fundo colorido — apenas texto, linhas e negrito.
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

from .models import PendingProduction


def _slug(texto: str) -> str:
    texto = texto.lower()
    substituicoes = {
        "á": "a", "à": "a", "ã": "a", "â": "a",
        "é": "e", "ê": "e", "í": "i",
        "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c",
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


def _build_pdf(caminho: Path, production: PendingProduction):
    """Constrói o PDF da lista de compras."""
    plano = production.plan or {}

    doc = SimpleDocTemplate(
        str(caminho),
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=f"Lista de Compras — Produção #{production.id}",
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
        f"LISTA DE COMPRAS — PRODUÇÃO #{production.id}", titulo,
    ))
    elementos.append(Paragraph(
        f"<b>Estabelecimento:</b> {production.store}<br/>"
        f"<b>Data de início:</b> "
        f"{plano.get('data_inicio', '—')[:16].replace('T', ' ')}<br/>"
        f"<b>Data de fim:</b> "
        f"{plano.get('data_fim', '—')[:16].replace('T', ' ')}",
        normal,
    ))
    elementos.append(Spacer(1, 0.4 * cm))

    # ---- Avisos ----
    avisos = plano.get("avisos", [])
    if avisos:
        elementos.append(Paragraph("Avisos", subtitulo))
        for a in avisos:
            elementos.append(Paragraph(f"⚠️  {a}", normal))
        elementos.append(Spacer(1, 0.4 * cm))

    # ---- Sub-produtos ----
    elementos.append(Paragraph("Sub-produtos a produzir", subtitulo))
    dados_sp = [["Sub-produto", "Quantidade", "Ajustado?"]]
    for sp in plano.get("sub_produtos", []):
        ajustado = "Sim" if sp.get("ajustado") else "—"
        dados_sp.append([
            sp["sub_product"],
            f'{_fmt(sp["quantity_final"], 3)} {sp["unit"]}',
            ajustado,
        ])
    t = Table(dados_sp, colWidths=[9 * cm, 5 * cm, 3 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#999999")),
        ("LINEBELOW", (0, 1), (-1, -2), 0.2, colors.HexColor("#DDDDDD")),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elementos.append(t)
    elementos.append(Spacer(1, 0.4 * cm))

    # ---- Cronograma ----
    elementos.append(Paragraph("Cronograma", subtitulo))
    dados_cr = [["Sub-produto", "Início", "Fim", "Duração"]]
    for c in plano.get("cronograma", []):
        dados_cr.append([
            c["sub_product"],
            c["inicio"][:16].replace("T", " "),
            c["fim"][:16].replace("T", " "),
            f'{_fmt(c["duracao_h"], 2)} h',
        ])
    t = Table(dados_cr, colWidths=[6 * cm, 4 * cm, 4 * cm, 3 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#999999")),
        ("LINEBELOW", (0, 1), (-1, -2), 0.2, colors.HexColor("#DDDDDD")),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elementos.append(t)
    elementos.append(Spacer(1, 0.4 * cm))

    # ---- Lista de compras ----
    elementos.append(Paragraph("Lista de compras", subtitulo))
    dados_lc = [["Insumo", "Quantidade", "Unidade", "Custo", "Obs."]]
    total = Decimal("0")
    for lc in plano.get("lista_compras", []):
        obs = "não-proporcional" if lc.get("not_proportional") else "—"
        custo = Decimal(str(lc.get("custo", "0")))
        total += custo
        dados_lc.append([
            lc["food_ingredient"],
            _fmt(lc["quantity"], 3),
            lc["unit"],
            f'R$ {_fmt(custo)}',
            obs,
        ])
    # Linha do total
    dados_lc.append(["", "", "", f'TOTAL: R$ {_fmt(total)}', ""])

    t = Table(
        dados_lc,
        colWidths=[6 * cm, 3 * cm, 2 * cm, 3 * cm, 3 * cm],
    )
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#999999")),
        ("LINEBELOW", (0, 1), (-1, -2), 0.2, colors.HexColor("#DDDDDD")),
        ("LINEABOVE", (0, -1), (-1, -1), 0.5, colors.HexColor("#999999")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elementos.append(t)

    # ---- Custo total ----
    elementos.append(Spacer(1, 0.4 * cm))
    custo = plano.get("custo", {})
    elementos.append(Paragraph(
        f"<b>Insumos:</b> R$ {_fmt(custo.get('insumos', '0'))}<br/>"
        f"<b>Energia:</b> R$ {_fmt(custo.get('energia', '0'))}<br/>"
        f"<b>Mão de obra:</b> R$ {_fmt(custo.get('mao_de_obra', '0'))}<br/>"
        f"<b>CUSTO TOTAL:</b> R$ {_fmt(custo.get('total', '0'))}",
        normal,
    ))

    doc.build(elementos)


def gerar_pdf_lista_compras(production_id: int) -> dict:
    """
    Gera o PDF da lista de compras de uma produção planejada.

    Devolve metadados: caminho, nome, url.
    """
    try:
        production = (
            PendingProduction.objects
            .select_related("store")
            .get(id=production_id)
        )
    except PendingProduction.DoesNotExist:
        raise ValueError(f"Produção {production_id} não encontrada.")

    if not production.plan:
        raise ValueError(
            f"Produção {production_id} ainda não foi planejada."
        )

    # Pasta: media/shopping_lists/
    pasta = Path(settings.MEDIA_ROOT) / "shopping_lists"
    pasta.mkdir(parents=True, exist_ok=True)

    # Nome: lista_compras_producao_4.pdf
    nome = f"lista_compras_producao_{production_id}.pdf"
    caminho = pasta / nome

    _build_pdf(caminho, production)

    relativo = caminho.relative_to(Path(settings.MEDIA_ROOT))
    url = f"{settings.MEDIA_URL}{relativo.as_posix()}"

    return {
        "production_id": production.id,
        "file": str(caminho),
        "filename": nome,
        "url": url,
    }