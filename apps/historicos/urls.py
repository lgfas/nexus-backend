from rest_framework.routers import DefaultRouter
from .views import HistoricoConsumoDemandaViewSet

router = DefaultRouter()
router.register(r'historicos-consumo-demanda', HistoricoConsumoDemandaViewSet, basename='historico-consumo-demanda')

urlpatterns = router.urls
