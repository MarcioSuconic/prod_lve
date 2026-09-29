"""
Django settings for lve project.

Gerencia a produção de produtos (compra de insumos, agendamento,
execução da receita e registro da produção).
"""

from pathlib import Path
import os

from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# ---------------------------------------------------------------------------
# Segurança
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY não definida no arquivo .env")

DEBUG = True            # TODO: ler de .env ao ir para produção
ALLOWED_HOSTS = ["*"]   # TODO: restringir em produção


# ---------------------------------------------------------------------------
# Aplicações
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # terceiros
    "rest_framework",
    "django_filters",

    # stories
    "apps.stories.store.apps.StoreConfig",
    "apps.stories.electric_power_x_store.apps.ElectricPowerXStoreConfig",
    "apps.stories.average_hourly_wage_x_store.apps.AverageHourlyWageXStoreConfig",

    # units
    "apps.units.physical_quantity.apps.PhysicalQuantityConfig",
    "apps.units.unit.apps.UnitConfig",

    # food_ingredients
    "apps.food_ingredients.supplier_food_ingredients.apps.SupplierFoodIngredientsConfig",
    "apps.food_ingredients.food_ingredient.apps.FoodIngredientConfig",
    "apps.food_ingredients.food_ingredient_density.apps.FoodIngredientDensityConfig",
    "apps.food_ingredients.food_ingredient_purchase.apps.FoodIngredientPurchaseConfig",
    "apps.food_ingredients.food_ingredient_portion.apps.FoodIngredientPortionConfig",

    # machinerys
    "apps.machinerys.machinery_scheduling.apps.MachinerySchedulingConfig",
    "apps.machinerys.machinery.apps.MachineryConfig",

    # recipe
    "apps.recipe.base_recipe.apps.BaseRecipeConfig",
    "apps.recipe.stage_base_recipe.apps.StageBaseRecipeConfig",
    "apps.recipe.operation_base_recipe.apps.OperationBaseRecipeConfig",
    "apps.recipe.execution_operation_base_recipe.apps.ExecutionOperationBaseRecipeConfig",

    # products
    "apps.products.product.apps.ProductConfig",
    "apps.products.product_x_sub_product.apps.ProductXSubProductConfig",    

    # sub_products
    "apps.sub_products.sub_product.apps.SubProdutoConfig",

    # products_div
    "apps.products_div.product_category.apps.ProductCategoryConfig",
    "apps.products_div.product_sub_category.apps.ProductSubCategoryConfig",
    "apps.products_div.sub_product_type.apps.SubProductTypeConfig",
    "apps.products_div.sub_product_sub_type.apps.SubProductSubTypeConfig",

    # productions
    "apps.productions.sub_product_production.apps.RegisterProductionSubProductsConfig",
    "apps.productions.product_production.apps.ProductProductionsConfig",
    ]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "lve.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "lve.wsgi.application"


# ---------------------------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
        "DISABLE_SERVER_SIDE_CURSORS": True,
    }
}


# ---------------------------------------------------------------------------
# Autenticação
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ---------------------------------------------------------------------------
# Internacionalização
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Arquivos estáticos
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"


# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}


# ---------------------------------------------------------------------------
# Chave primária padrão
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"