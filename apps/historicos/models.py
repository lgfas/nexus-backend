from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.clientes.models import Cliente

class HistoricoConsumoDemanda(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='historicos_consumo_demanda'
    )

    # Mês como número (1-12)
    mes = models.IntegerField(
        validators=[
            MinValueValidator(1),  # Janeiro
            MaxValueValidator(12) # Dezembro
        ]
    )

    # DEMANDA MEDIDA
    demanda_medida_ponta = models.FloatField(validators=[MinValueValidator(0.0)], blank=True, null=True)
    demanda_medida_fora_ponta = models.FloatField(validators=[MinValueValidator(0.0)], blank=True, null=True)
    demanda_medida_reativo_excedente = models.FloatField(validators=[MinValueValidator(0.0)], blank=True, null=True)

    # CONSUMO FATURADO
    consumo_faturado_ponta_tot = models.FloatField(validators=[MinValueValidator(0.0)], blank=True, null=True)
    consumo_faturado_fora_ponta = models.FloatField(validators=[MinValueValidator(0.0)], blank=True, null=True)
    consumo_faturado_reativo_excedente = models.FloatField(validators=[MinValueValidator(0.0)], blank=True, null=True)

    # HORÁRIO RESERVADO
    horario_reservado_consumo = models.FloatField(validators=[MinValueValidator(0.0)], blank=True, null=True)
    horario_reservado_reativo_excedente = models.FloatField(validators=[MinValueValidator(0.0)], blank=True, null=True)

    def __str__(self):
        return f"Histórico {self.cliente.nome} - Mês {self.mes}"
