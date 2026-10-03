from rest_framework.routers import DefaultRouter

from .views import NFPurchaseViewSet

router = DefaultRouter()
router.register(r"nf-purchases", NFPurchaseViewSet, basename="nf-purchase")

urlpatterns = router.urls