from rest_framework.routers import DefaultRouter
from .views import ContaEnergiaViewSet, ItensFaturaViewSet, UploadFaturaAPIView
from django.urls import path

router = DefaultRouter()
router.register(r'contas-energia', ContaEnergiaViewSet, basename='contaenergia')
router.register(r'itens-fatura', ItensFaturaViewSet, basename='itensfatura')

urlpatterns = router.urls + [
    path('upload-fatura/', UploadFaturaAPIView.as_view(), name='upload-fatura'),
]
