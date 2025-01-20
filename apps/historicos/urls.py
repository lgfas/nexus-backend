from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import HistoricoConsumoDemandaViewSet, HistoricoAPIView

router = DefaultRouter()
router.register(r'historicos-consumo-demanda', HistoricoConsumoDemandaViewSet, basename='historico-consumo-demanda')

urlpatterns = router.urls + [
    path('extrair-historico-fatura/', HistoricoAPIView.as_view(), name='extrair-historico-fatura'),
]