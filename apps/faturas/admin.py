from django.contrib import admin
from .models import ContaEnergia, ItemFatura, ItemFinanceiro


@admin.register(ContaEnergia)
class ContaEnergiaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'cliente', 'mes', 'vencimento', 'total_pagar',
        'leitura_anterior', 'leitura_atual', 'numero_dias', 'proxima_leitura'
    )
    search_fields = ('cliente__nome', 'mes', 'vencimento')
    list_filter = ('cliente__estado', 'mes')
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


@admin.register(ItemFinanceiro)
class ItemFinanceiroAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'conta_energia', 'descricao', 'valor'
    )
    search_fields = ('conta_energia__cliente__nome', 'descricao')
    list_filter = ('conta_energia__mes',)
    ordering = ('conta_energia',)
