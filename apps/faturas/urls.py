from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ContaEnergiaViewSet, ItemFaturaViewSet, UploadFaturaAPIView, TributoViewSet, ItensFaturaAPIView

router = DefaultRouter()
router.register(r'contas-energia', ContaEnergiaViewSet, basename='contaenergia')
router.register(r'itens-fatura', ItemFaturaViewSet, basename='itemfatura')
router.register(r'tributos', TributoViewSet, basename='tributo')

urlpatterns = router.urls + [
    path('upload-fatura/', UploadFaturaAPIView.as_view(), name='upload-fatura'),
    path('extrair-itens-fatura/', ItensFaturaAPIView.as_view(), name='extrair-itens-fatura'),
]
