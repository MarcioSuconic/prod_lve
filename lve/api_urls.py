from rest_framework.routers import DefaultRouter

from apps.units.physical_quantity.views import PhysicalQuantityViewSet
from apps.units.unit.views import UnitViewSet

router = DefaultRouter()
router.register("physical-quantities", PhysicalQuantityViewSet, basename="physical-quantity")
router.register("units", UnitViewSet, basename="unit")

urlpatterns = router.urls