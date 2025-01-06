from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# Configuração do Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Documentação da API",
        default_version='v1',
        description="Documentação do backend do projeto Nexus",
        terms_of_service="https://www.seusite.com/termos/",
        contact=openapi.Contact(email="suporte@seusite.com"),
        license=openapi.License(name="Licença MIT"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/clientes/', include('apps.clientes.urls')),
    path('api/faturas/', include('apps.faturas.urls')),
    path('api/parceiros/', include('apps.parceiros.urls')),
    path('api/historicos/', include('apps.historicos.urls')),
    path('api/tarifas/', include('apps.tarifas.urls')),

    # Documentação com Swagger e ReDoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
