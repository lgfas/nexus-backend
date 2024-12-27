from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DistribuidoraViewSet, TarifaViewSet, UploadTarifasCSVAPIView, AtualizarTarifasAPIView

# Configuração do Router
router = DefaultRouter()
router.register(r'distribuidoras', DistribuidoraViewSet, basename='distribuidora')
router.register(r'tarifas', TarifaViewSet, basename='tarifa')

# Configuração das URLs
urlpatterns = router.urls + [
    path('upload-csv/', UploadTarifasCSVAPIView.as_view(), name='upload-csv'),
    path('atualizar/', AtualizarTarifasAPIView.as_view(), name='atualizar-tarifas'),
]
