from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.clientes.urls')),
    path('api/', include('apps.faturas.urls')),
    path('api/', include('apps.parceiros.urls')),
    path('api/', include('apps.historicos.urls')),
]
