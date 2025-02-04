from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CalcularMelhoriaModalidadeAPIView, CalcularMelhorConsumoAnualAPIView, CalcularMelhorDemandaAPIView, \
    CalcularMelhorModalidadeAPIView
from .views import ContaEnergiaViewSet, ItemFaturaViewSet, UploadFaturaAPIView, TributoViewSet, ItensFaturaAPIView

router = DefaultRouter()
router.register(r'contas-energia', ContaEnergiaViewSet, basename='contaenergia')
router.register(r'itens-fatura', ItemFaturaViewSet, basename='itemfatura')
router.register(r'tributos', TributoViewSet, basename='tributo')

urlpatterns = router.urls + [
    path('upload-fatura/', UploadFaturaAPIView.as_view(), name='upload-fatura'),
    path('calcular-melhoria-modalidade/<int:conta_id>/', CalcularMelhoriaModalidadeAPIView.as_view(),
         name='calcular_melhoria_modalidade'),
    path('extrair-itens-fatura/', ItensFaturaAPIView.as_view(), name='extrair-itens-fatura'),
    path('calcular-melhor-consumo-anual/<int:conta_id>/', CalcularMelhorConsumoAnualAPIView.as_view(),
         name='calcular_melhor_consumo_anual'),
    path('calcular-melhor-demanda/<int:conta_id>/', CalcularMelhorDemandaAPIView.as_view(),
         name='calcular_melhor_demanda'),
    path('calcular-melhor-modalidade/<int:conta_id>/', CalcularMelhorModalidadeAPIView.as_view(),
         name='calcular_melhor_modalidade'),
]
