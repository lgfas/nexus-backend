from django.contrib import admin
from .models import Distribuidora, Tarifa


@admin.register(Distribuidora)
class DistribuidoraAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'estado')
    search_fields = ('nome', 'estado')


@admin.register(Tarifa)
class TarifaAdmin(admin.ModelAdmin):
    list_display = ('distribuidora', 'data_inicio_vigencia', 'modalidade', 'subgrupo', 'tipo_tarifa', 'valor_tusd', 'valor_te')
    list_filter = ('distribuidora', 'modalidade', 'subgrupo')
    search_fields = ('distribuidora__nome',)
