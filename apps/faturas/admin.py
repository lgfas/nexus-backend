from django.contrib import admin

from .models import ContaEnergia, ItemFatura, Tributo


@admin.register(ContaEnergia)
class ContaEnergiaAdmin(admin.ModelAdmin):
    list_display = (
        'cliente', 'mes', 'vencimento', 'total_pagar',
        'leitura_anterior', 'leitura_atual', 'proxima_leitura',
        'subgrupo', 'tipo_tarifa_bt', 'tipo_tarifa_at',
        'demanda_contratada_unica', 'demanda_contratada_ponta', 'demanda_contratada_fora_ponta',
        'fator_potencia'
    )
    search_fields = ('cliente__nome', 'mes', 'vencimento', 'subgrupo')
    list_filter = ('subgrupo', 'tipo_tarifa_bt', 'tipo_tarifa_at')
    ordering = ('-mes',)

@admin.register(ItemFatura)
class ItemFaturaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'conta_energia', 'descricao', 'quantidade',
        'preco_unitario', 'tarifa', 'pis_cofins', 'icms', 'valor'
    )
    search_fields = ('conta_energia__cliente__nome', 'descricao')
    list_filter = ('conta_energia__mes',)
    ordering = ('conta_energia',)

@admin.register(Tributo)
class TributoAdmin(admin.ModelAdmin):
    list_display = ("conta_energia", "tipo", "base", "aliquota", "valor")
    list_filter = ("tipo",)
    search_fields = ("conta_energia__cliente__nome", "tipo")

