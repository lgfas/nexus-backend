from rest_framework.routers import DefaultRouter
from .views import ContaEnergiaViewSet, ItensFaturaViewSet

router = DefaultRouter()
router.register(r'contas-energia', ContaEnergiaViewSet, basename='contaenergia')
router.register(r'itens-fatura', ItensFaturaViewSet, basename='itensfatura')

urlpatterns = router.urls
