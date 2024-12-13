from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/clientes/', include('apps.clientes.urls')),
    path('api/faturas/', include('apps.faturas.urls')),  # Faturas com prefixo exclusivo
    path('api/parceiros/', include('apps.parceiros.urls')),
    path('api/historicos/', include('apps.historicos.urls')),  # Historicos com prefixo exclusivo
]
