from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ContaEnergiaViewSet, ItemFaturaViewSet, UploadFaturaAPIView

router = DefaultRouter()
router.register(r'contas-energia', ContaEnergiaViewSet, basename='contaenergia')
router.register(r'itens-fatura', ItemFaturaViewSet, basename='itemfatura')

urlpatterns = router.urls + [
    path('upload-fatura/', UploadFaturaAPIView.as_view(), name='upload-fatura'),
]
