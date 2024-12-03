from django.contrib import admin
from .models import ContaEnergia, ItensFatura

@admin.register(ContaEnergia)
class ContaEnergiaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'mes', 'vencimento', 'total_pagar', 'leitura_anterior', 'leitura_atual')
    search_fields = ('cliente__nome', 'mes', 'vencimento')
    list_filter = ('cliente__estado', 'mes')
    ordering = ('-mes',)

@admin.register(ItensFatura)
class ItensFaturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'conta_energia', 'consumo_ponta', 'consumo_fora_ponta', 'demanda_ativa')
    search_fields = ('conta_energia__cliente__nome',)
    list_filter = ('conta_energia__mes',)
    ordering = ('conta_energia',)
