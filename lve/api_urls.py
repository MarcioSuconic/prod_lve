from rest_framework.routers import DefaultRouter

from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from apps.units.physical_quantity.views import PhysicalQuantityViewSet
from apps.units.unit.views import UnitViewSet

from apps.stories.store.views import StoreViewSet

from apps.products_div.product_category.views import ProductCategoryViewSet
from apps.products_div.product_sub_category.views import ProductSubCategoryViewSet
from apps.products_div.sub_product_type.views import SubProductTypeViewSet
from apps.products_div.sub_product_sub_type.views import SubProductSubTypeViewSet

from apps.food_ingredients.supplier_food_ingredients.views import SupplierFoodIngredientsViewSet
from apps.food_ingredients.food_ingredient.views import FoodIngredientViewSet
from apps.food_ingredients.food_ingredient_density.views import FoodIngredientDensityViewSet

from apps.stories.electric_power_x_store.views import ElectricPowerXStoreViewSet
from apps.stories.average_hourly_wage_x_store.views import AverageHourlyWageXStoreViewSet

from apps.machinerys.machinery.views import MachineryViewSet
from apps.machinerys.machinery_scheduling.views import MachinerySchedulingViewSet

from apps.recipe.base_recipe.views import BaseRecipeViewSet
from apps.recipe.stage_base_recipe.views import StageBaseRecipeViewSet
from apps.recipe.operation_base_recipe.views import OperationBaseRecipeViewSet
from apps.recipe.execution_operation_base_recipe.views import ExecutionOperationBaseRecipeViewSet

from apps.sub_products.sub_product.views import SubProductViewSet

from apps.products.product.views import ProductViewSet
from apps.products.product_x_sub_product.views import ProductXSubProductViewSet
from apps.productions.product_production.views import (
    RegisterProductionProductsViewSet,
    FeedBackProductionProductsViewSet,
)

from apps.productions.sub_product_production.views import (
    RegisterProductionSubProductsViewSet,
    FeedBackProductionSubProductsViewSet,
)

from apps.food_ingredients.food_ingredient_purchase.views import (
    FoodIngredientPurchaseViewSet,
)

from apps.food_ingredients.food_ingredient_portion.views import (
    FoodIngredientPortionViewSet,
)

from apps.machinerys.machinery.views import MachineryViewSet

from apps.food_ingredients.nf_purchase.views import NFPurchaseViewSet

from apps.utensils.utensil.views import UtensilViewSet

router = DefaultRouter()

# units
router.register("physical-quantities", PhysicalQuantityViewSet, basename="physical-quantity")
router.register("units", UnitViewSet, basename="unit")

# stories
router.register("stores", StoreViewSet, basename="store")

# products_div
router.register("product-categories", ProductCategoryViewSet, basename="product-category")
router.register("product-sub-categories", ProductSubCategoryViewSet, basename="product-sub-category")
router.register("sub-product-types", SubProductTypeViewSet, basename="sub-product-type")
router.register("sub-product-sub-types", SubProductSubTypeViewSet, basename="sub-product-sub-type")

# food_ingredients
router.register("suppliers", SupplierFoodIngredientsViewSet, basename="supplier")
router.register("food-ingredients", FoodIngredientViewSet, basename="food-ingredient")
router.register("food-ingredient-densities", FoodIngredientDensityViewSet, basename="food-ingredient-density")
router.register(
    "food-ingredient-purchases",
    FoodIngredientPurchaseViewSet,
    basename="food-ingredient-purchase",
)
router.register(
    "nf-purchases",
    NFPurchaseViewSet,
    basename="nf-purchase",
)

# stories extras
router.register("electric-power-fares", ElectricPowerXStoreViewSet, basename="electric-power-fare")
router.register("average-hourly-wages", AverageHourlyWageXStoreViewSet, basename="average-hourly-wage")

# machinerys
router.register("machineries", MachineryViewSet, basename="machinery")
router.register("machinery-schedules", MachinerySchedulingViewSet, basename="machinery-schedule")
#router.register("utensils", UtensilViewSet, basename="utensil")

# utensils
router.register("utensils", UtensilViewSet, basename="utensil")

# recipe
router.register("base-recipes", BaseRecipeViewSet, basename="base-recipe")
router.register("stage-base-recipes", StageBaseRecipeViewSet, basename="stage-base-recipe")
router.register("operation-base-recipes", OperationBaseRecipeViewSet, basename="operation-base-recipe")
router.register(
    "execution-operation-base-recipes",
    ExecutionOperationBaseRecipeViewSet,
    basename="execution-operation-base-recipe",
)

# sub_products
router.register("sub-products", SubProductViewSet, basename="sub-product")

# products
router.register("products", ProductViewSet, basename="product")
router.register("product-x-sub-products", ProductXSubProductViewSet, basename="product-x-sub-product")
router.register(
    "register-production-products",
    RegisterProductionProductsViewSet,
    basename="register-production-product",
)
router.register(
    "feedback-production-products",
    FeedBackProductionProductsViewSet,
    basename="feedback-production-product",
)

# productions
router.register(
    "register-production-sub-products",
    RegisterProductionSubProductsViewSet,
    basename="register-production-sub-product",
)
router.register(
    "feedback-production-sub-products",
    FeedBackProductionSubProductsViewSet,
    basename="feedback-production-sub-product",
)

router.register(
    "food-ingredient-portions",
    FoodIngredientPortionViewSet,
    basename="food-ingredient-portion",
)

urlpatterns = router.urls + [
    path("api-token-auth/", obtain_auth_token, name="api-token-auth"),
]