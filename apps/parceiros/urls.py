from rest_framework.routers import DefaultRouter
from .views import ParceiroViewSet

router = DefaultRouter()
router.register(r'parceiros', ParceiroViewSet, basename='parceiro')

urlpatterns = router.urls
