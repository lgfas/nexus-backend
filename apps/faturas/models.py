from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from apps.clientes.models import Cliente
from datetime import date

class ContaEnergia(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='contas_energia')
    mes = models.DateField(help_text='Data referente ao mês de consumo (use o primeiro dia do mês).')
    vencimento = models.DateField()
    total_pagar = models.DecimalField(max_digits=10, decimal_places=2)
    leitura_anterior = models.FloatField(validators=[MinValueValidator(0.0)])
    leitura_atual = models.FloatField(validators=[MinValueValidator(0.0)])
    numero_dias = models.PositiveIntegerField()
    proxima_leitura = models.DateField()
    demanda_contratada = models.FloatField()

    def clean(self):
        super().clean()
        # Validação de leituras
        if self.leitura_atual < self.leitura_anterior:
            raise ValidationError('A leitura atual não pode ser menor que a leitura anterior.')
        # Validação de datas
        if self.vencimento < self.mes:
            raise ValidationError('A data de vencimento não pode ser anterior ao mês de referência.')
        if self.proxima_leitura <= date.today():
            raise ValidationError('A data da próxima leitura deve ser futura.')

    def __str__(self):
        return f"Conta de Energia - {self.cliente.nome} - {self.mes.strftime('%m/%Y')}"


class ItensFatura(models.Model):
    conta_energia = models.ForeignKey(ContaEnergia, on_delete=models.CASCADE, related_name='itens_fatura')
    consumo_ponta = models.FloatField(validators=[MinValueValidator(0.0)])
    consumo_fora_ponta = models.FloatField(validators=[MinValueValidator(0.0)])
    consumo_compensado_fp = models.FloatField(validators=[MinValueValidator(0.0)], blank=True, null=True)
    energia_ativa_injetada_fp = models.FloatField(validators=[MinValueValidator(0.0)], blank=True, null=True)
    demanda_ativa_isenta_icms = models.FloatField(validators=[MinValueValidator(0.0)], blank=True, null=True)
    demanda_ativa = models.FloatField(validators=[MinValueValidator(0.0)])
    consumo_reativo_excedente_np = models.FloatField(validators=[MinValueValidator(0.0)], blank=True, null=True)
    consumo_reativo_excedente_fp = models.FloatField(validators=[MinValueValidator(0.0)], blank=True, null=True)
    adicional_bandeira = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Itens da Fatura - Conta ID {self.conta_energia.id}"

