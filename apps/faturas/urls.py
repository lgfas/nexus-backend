from rest_framework.routers import DefaultRouter
from .views import ContaEnergiaViewSet, ItemFaturaViewSet, ItemFinanceiroViewSet, UploadFaturaAPIView
from django.urls import path

router = DefaultRouter()
router.register(r'contas-energia', ContaEnergiaViewSet, basename='contaenergia')
router.register(r'itens-fatura', ItemFaturaViewSet, basename='itemfatura')
router.register(r'itens-financeiros', ItemFinanceiroViewSet, basename='itemfinanceiro')

urlpatterns = router.urls + [
    path('upload-fatura/', UploadFaturaAPIView.as_view(), name='upload-fatura'),
]
