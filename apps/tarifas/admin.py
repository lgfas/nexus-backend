from django.contrib import admin

from .models import Distribuidora, Tarifa


@admin.register(Distribuidora)
class DistribuidoraAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'estado')  # Exibe os principais campos
    search_fields = ('nome', 'estado', 'codigo')  # Pesquisa pelos campos principais


@admin.register(Tarifa)
class TarifaAdmin(admin.ModelAdmin):
    list_display = (
        'distribuidora',
        'data_inicio_vigencia',
        'data_fim_vigencia',
        'modalidade',
        'subgrupo',
        'tipo_tarifa',
        'valor_tusd',
        'valor_te',
        'dsc_reh',
        'dsc_classe',
        'dsc_subclasse',
        'dsc_detalhe',
        'nom_posto_tarifario',
        'dsc_unidade_terciaria'
    )
    list_filter = (
        'distribuidora',
        'data_inicio_vigencia',
        'data_fim_vigencia',
        'modalidade',
        'subgrupo',
        'tipo_tarifa',
        'nom_posto_tarifario',
    )
    search_fields = (
        'distribuidora__nome',
        'modalidade',
        'subgrupo',
        'tipo_tarifa',
        'dsc_reh',
        'dsc_classe',
        'dsc_subclasse',
        'dsc_detalhe',
        'nom_posto_tarifario',
        'dsc_unidade_terciaria'
    )
    list_per_page = 50
    ordering = ('-data_inicio_vigencia',)

