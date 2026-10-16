# LVE — Sistema de Produção

Sistema de gestão de produção para lanchonete: cadastro de insumos, receitas,
produtos, sub-produtos, cronograma de produção, custo, ficha técnica e
planejamento de batidas.

**Contato:** advmsuconic@gmail.com

---

## Sumário

1. [Visão geral](#visão-geral)
2. [Stack](#stack)
3. [Como rodar](#como-rodar)
4. [Arquitetura](#arquitetura)
5. [Fluxo de operação](#fluxo-de-operação)
6. [Endpoints principais](#endpoints-principais)
7. [Mídia (PDFs)](#mídia-pdfs)
8. [Backup e restore](#backup-e-restore)
9. [Pendências e roadmap](#pendências-e-roadmap)

---

## Visão geral

O sistema cobre o ciclo completo de produção de uma lanchonete:

- **Cadastro** de insumos, fornecedores, NF, receitas, produtos, sub-produtos
- **Custeio** de receita (insumos + energia + mão de obra) e produto (com markup)
- **Ficha técnica** em PDF (com peso, incorporação, custos, preço)
- **Cronograma reverso** de produção (timing dos sub-produtos)
- **Planejamento de batidas** (consolidação de sub-produtos + arredondamento)
- **Lista de compras** em PDF
- **Auditoria automática** ao iniciar o servidor

---

## Stack

| Componente | Versão |
|---|---|
| Python | 3.14.7 |
| Django | 6.1.1 |
| Django REST Framework | (requirements.txt) |
| PostgreSQL | (local) |
| ReportLab | (para PDFs) |

**Frontend:** tkinter (`lve_nf` — projeto separado).

---

## Como rodar

### 1. Requisitos

- Python 3.14+
- PostgreSQL 14+
- (Linux) `libpq-dev` (para psycopg)

### 2. Setup

```bash
cd /home/marcio/Desktop/projetos/app_prod_lve
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

3. Configurar .env
Cria o arquivo .env na raiz com:

text
SECRET_KEY=uma-chave-secreta-bem-longa
DEBUG=True
DB_NAME=lve
DB_USER=marcio_gcs
DB_PASSWORD=****
DB_HOST=localhost
DB_PORT=5432
4. Banco de dados
bash
# Cria o banco (uma vez)
createdb -U marcio_gcs -h localhost -p 5432 lve

# Aplica as migrações
python manage.py migrate

# Cria superusuário (opcional)
python manage.py createsuperuser
5. Rodar
bash
python manage.py runserver
Ao subir, o sistema imprime uma auditoria:

text
============================================================
⚠️  AUDITORIA — TAREFAS PENDENTES
============================================================

🟡 Insumos de volume sem densidade:
   - Água (l)

🟠 Receitas com balanço de massa ruim:
   - massa de pão de queijo: input=2188g, output=2500g (-14,26%)

============================================================
Se estiver tudo OK: ✅ Auditoria: tudo OK.

Arquitetura
Estrutura de pastas
text
app_prod_lve/
├── apps/
│   ├── units/                  # Grandezas físicas e unidades
│   ├── food_ingredients/       # Insumos, densidade, porção, compras, NF
│   ├── products_div/           # Categorias, subcategorias, tipos
│   ├── products/               # Produtos, vínculos com sub-produtos
│   ├── sub_products/           # Sub-produtos
│   ├── recipe/                 # Receita base, etapa, operação, execução
│   ├── stories/                # Loja, tarifa de energia, salário/hora
│   ├── machinerys/             # Maquinário e scheduling
│   ├── utensils/               # Utensílios e scheduling
│   ├── productions/            # Planejamento e execução de produção
│   │   ├── pending_production/     # Produções pendentes + PDF
│   │   ├── production_x_product/   # Itens da produção
│   │   ├── product_production/     # Registro de produção de produto
│   │   ├── sub_product_production/ # Registro de produção de sub-produto
│   │   └── production_input/       # Input real (calibração)
│   └── audit/                  # Auditoria automática
├── lve/
│   ├── settings.py
│   ├── urls.py
│   └── api_urls.py
├── media/
│   ├── tech_sheets/            # Fichas técnicas em PDF
│   └── shopping_lists/         # Listas de compras em PDF
├── backups/                    # Backups do banco (não versionado)
├── backup.sh                   # Script de backup
└── manage.py
Modelo de domínio (simplificado)
text
UNIT
 └── PhysicalQuantity (massa, volume, unidade, potência, ...)

FOOD_INGREDIENT (insumo)
 ├── FoodIngredientDensity    (massa <-> volume)
 ├── FoodIngredientPortion    (contagem <-> massa/volume)
 ├── FoodIngredientPurchase   (compra, com unit_price derivado)
 └── NFPurchase               (nota fiscal com N itens)

BASE_RECIPE (receita base, "rende N unidade")
 ├── StageBaseRecipe           (etapa: Preparo, Mistura, Assar)
 ├── OperationBaseRecipe       (operação: Sovar, Fornear)
 └── ExecutionOperationBaseRecipe (passo: etapa + operação + insumo + tempo
                                    + incorporação + temperatura + pH
                                    + maquinário + utensílio)

SUB_PRODUCT (sub-produto)
 ├── base_recipe (FK)
 └── sub_product_sub_type (FK)

PRODUCT (produto)
 ├── store (FK)
 ├── sub_category (FK)
 ├── production_capacity      (capacidade por batida)
 ├── default_production       (produção padrão)
 └── via Product_x_Sub_Product:
      ├── sub_product (FK)
      ├── composition_percentage
      ├── at_start / at_finish / after_to
      ├── relative_to (FK pra si mesmo)
      ├── elapsed_time
      └── elapsed_signal (+/-)

PRODUCTION
 ├── PendingProduction        (lista de espera + plano calculado)
 │    └── ProductionXProduct  (itens: produto + quantidade)
 ├── RegisterProductionSubProducts (o que foi produzido de fato)
 ├── RegisterProductionProducts    (idem, para produto)
 └── ProductionInput              (input real, para calibrar incorporação)
Cálculos principais
1. Custo de receita (apps/recipe/base_recipe/services.py)

text
custo_insumos  = Σ (qtde_convertida × unit_price da última compra)
custo_energia  = Σ (potência_kW × tempo_h × tarifa_kWh)
custo_mão_obra = Σ (labor_minutes da operação / 60 × salário_hora)
2. Custo de produto (apps/products/product/cost.py)

text
custo_por_grama = custo_receita / size_receita
custo_produto   = custo_por_grama × (peso × composition_percentage / 100)
preco_sugerido  = custo_produto × (1 + markup/100)
preco_final     = PriceRounder.round(preco_sugerido)
3. Balanço de massa (apps/recipe/base_recipe/services.py)

text
peso_input  = Σ (qtde_em_gramas × incorporation_percentage / 100)
peso_output = size da receita (em gramas)
diferença   = peso_input − peso_output
classificação:
   input < output → "erro"
   0% a -5%       → "ok"
   -5% a -15%     → "atencao"
   < -15%         → "suspeito"
4. Cronograma reverso (apps/products/product/services.py)

text
Para cada sub-produto no produto:
  se at_start:   referência = início do relativo
  se at_finish:  referência = fim do relativo
  se after_to:   referência = fim do relativo (início imediato)
  senão:         referência = início da produção

  aplicar elapsed_time (sinal +/-)
  se at_finish:  fim = ponto, início = fim − duração
  senão:         início = ponto, fim = início + duração
5. Planejamento de produção (apps/productions/pending_production/services.py)

text
1. Expandir produtos em sub-produtos
2. Consolidar por sub-produto (somar quantidades)
3. Arredondar não-proporcionais (múltiplos inteiros)
4. Calcular cronograma
5. Calcular custo (soma das receitas escaladas)
6. Montar lista de compras (consolidada)
Fluxo de operação
Cadastro (uma vez)
text
1. Cadastrar Unidades (kg, g, l, ml, un, ...)
2. Cadastrar Fornecedores
3. Cadastrar Insumos (com densidade se volume)
4. Cadastrar NF (compra de insumos)
5. Cadastrar Etapas e Operações
6. Cadastrar Receitas Base
7. Cadastrar Categorias e Subcategorias
8. Cadastrar Tipos e Subtipos
9. Cadastrar Sub-produtos
10. Cadastrar Produtos (com composição + timing)
11. Cadastrar Maquinário e Utensílios
12. Cadastrar Loja, Tarifa de Energia, Salário/Hora
Operação (recorrente)
text
1. Tela 1 — Cadastrar produções pendentes
   └── Adiciona produtos + quantidades à lista de espera

2. Tela 2 — Planejar produção
   ├── Seleciona itens + data/hora
   ├── Calcula plano (sub-produtos, cronograma, custo, lista de compras)
   └── Salva como 'scheduled'

3. Imprimir lista de compras (PDF) e ir às compras

4. Produzir de verdade (o sistema ainda não registra a execução
   automaticamente — roadmap)

5. Gerar ficha técnica dos produtos (PDF)

6. Calcular custo e preço com markup
Endpoints principais
Autenticação
text
POST /api/api-token-auth/         → devolve token
Cadastros
text
/api/physical-quantities/         → grandezas físicas
/api/units/                        → unidades
/api/stores/                       → lojas
/api/suppliers/                    → fornecedores
/api/food-ingredients/             → insumos
/api/food-ingredient-densities/    → densidades
/api/food-ingredient-purchases/    → compras
/api/food-ingredient-portions/     → porções
/api/nf-purchases/                 → notas fiscais
/api/product-categories/           → categorias de produto
/api/product-sub-categories/       → subcategorias
/api/sub-product-types/            → tipos de sub-produto
/api/sub-product-sub-types/        → subtipos
/api/sub-products/                 → sub-produtos
/api/products/                     → produtos
/api/product-x-sub-products/       → vínculo produto x sub-produto
/api/stage-base-recipes/           → etapas
/api/operation-base-recipes/       → operações
/api/base-recipes/                 → receitas base
/api/execution-operation-base-recipes/  → execuções
/api/machineries/                  → maquinário
/api/utensils/                     → utensílios
/api/electric-power-fares/         → tarifas de energia
/api/hourly-wages/                 → salários/hora
Custeio
text
GET /api/base-recipes/{id}/cost/       → custo da receita
GET /api/products/{id}/unit-cost/      → custo unitário + preço
GET /api/products/{id}/cost/?quantity=N&unit=X → custo de produção
GET /api/products/{id}/schedule/?start=DATA → cronograma
POST /api/products/{id}/tech-sheet/    → gera ficha técnica (PDF)
GET  /api/products/{id}/tech-sheet/download/ → baixa ficha técnica
Produção
text
/api/pending-productions/                → CRUD de produções pendentes
/api/pending-productions/{id}/add-item/  → adiciona item
/api/pending-productions/{id}/remove-item/ → remove item
/api/pending-productions/{id}/plan/      → planeja (calcula + salva)
/api/pending-productions/{id}/shopping-list.pdf/ → gera lista de compras
/api/production-x-products/              → itens das produções
Auditoria
text
GET /api/audit/full/     → auditoria completa
GET /api/audit/startup/  → resumo (usado no startup)
Mídia (PDFs)
Fichas técnicas:

text
media/tech_sheets/pao_de_queijo_v1.pdf
media/tech_sheets/pao_de_queijo_v2.pdf
...
Versionadas. Cada geração cria uma nova versão.

Listas de compras:

text
media/shopping_lists/lista_compras_producao_4.pdf
media/shopping_lists/lista_compras_producao_10.pdf
Sobrescritas. Uma por produção.

Configuração (settings.py):

python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
Backup e restore
Backup manual
bash
cd ~/Desktop/projetos/app_prod_lve

PGPASSWORD='3737_Mgcs' pg_dump -U marcio_gcs -h localhost -p 5432 \
  -d lve -F c -f backups/lve_$(date +%Y-%m-%d_%H-%M).dump
Backup automático
Script: ./backup.sh

Agendar no cron (diário às 3h):

bash
crontab -e
Adicionar:

text
0 3 * * * /home/marcio/Desktop/projetos/app_prod_lve/backup.sh >> /home/marcio/Desktop/projetos/app_prod_lve/backups/backup.log 2>&1
Restore
bash
# Cria um banco de teste
createdb -U marcio_gcs -h localhost -p 5432 lve_teste

# Restaura
PGPASSWORD='3737_Mgcs' pg_restore -U marcio_gcs -h localhost -p 5432 \
  -d lve_teste backups/lve_XXXX.dump

# Confere
PGPASSWORD='3737_Mgcs' psql -U marcio_gcs -h localhost -p 5432 \
  -d lve_teste -c "\dt"

# Apaga o banco de teste
dropdb -U marcio_gcs -h localhost -p 5432 lve_teste
Pendências e roadmap
Curto prazo (antes de inaugurar)
□ Rodar em produção (DEBUG=False, ALLOWED_HOSTS, SECRET_KEY seguro)
□ Cadastrar o menu real (20-30 produtos)
□ Documentação da UI (lve_nf)
□ Backup automático agendado
Médio prazo (depois de inaugurar)
□ Execução de produção — criar RegisterProductionSubProducts automaticamente ao confirmar
□ Integração com machinery_scheduling — agenda de maquinário e utensílios
□ Tela de histórico de produções
□ Estoque de insumos (quando a dor for real)
Longo prazo
□ Múltiplas lojas
□ App mobile / web
□ Automação de compras (baseado em estoque e produção)
□ Relatórios (custo médio por produto, margem, etc)
Licença
Uso interno.

text

---

## Próximo passo

**Cola o `README.md` acima no `app_prod_lve/README.md`.**

Depois eu mando o **`README.md` do `lve_nf`** (o frontend).

**Confirma que colou?** 🚀