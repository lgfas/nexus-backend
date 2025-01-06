from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.clientes.models import Cliente


class ContaEnergia(models.Model):
    # Subgrupo: BT ou AT
    SUBGRUPO_CHOICES = [
        ('BT', 'Baixa Tensão'),
        ('AT', 'Alta Tensão'),
    ]

    # Tipos de tarifa para Alta Tensão (AT)
    TIPO_TARIFA_AT_CHOICES = [
        ('Verde', 'Verde'),
        ('Azul', 'Azul'),
    ]

    # Tipos de tarifa para Baixa Tensão (BT)
    TIPO_TARIFA_BT_CHOICES = [
        ('Convencional', 'Convencional'),
        ('Branca', 'Branca'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='contas_energia')
    mes = models.DateField(help_text='Data referente ao mês de consumo (use o primeiro dia do mês).')
    vencimento = models.DateField()
    total_pagar = models.DecimalField(max_digits=10, decimal_places=2)

    # Campos ajustados para 'date'
    leitura_anterior = models.DateField(help_text='Data da leitura anterior.')
    leitura_atual = models.DateField(help_text='Data da leitura atual.')
    proxima_leitura = models.DateField(help_text='Data programada para a próxima leitura.')

    numero_dias = models.PositiveIntegerField()

    # Subgrupo
    subgrupo = models.CharField(max_length=2, choices=SUBGRUPO_CHOICES, default='BT')

    # Tipos de tarifa por subgrupo
    tipo_tarifa_bt = models.CharField(
        max_length=15,
        choices=TIPO_TARIFA_BT_CHOICES,
        blank=True,
        null=True,
        help_text='Usado apenas para subgrupo BT (Baixa Tensão).'
    )
    tipo_tarifa_at = models.CharField(
        max_length=10,
        choices=TIPO_TARIFA_AT_CHOICES,
        blank=True,
        null=True,
        help_text='Usado apenas para subgrupo AT (Alta Tensão).'
    )

    # Demanda contratada
    demanda_contratada_unica = models.FloatField(
        validators=[MinValueValidator(0.0)],
        blank=True,
        null=True,
        help_text='Preencher apenas para tarifa verde (Alta Tensão).'
    )
    demanda_contratada_ponta = models.FloatField(
        validators=[MinValueValidator(0.0)],
        blank=True,
        null=True,
        help_text='Preencher apenas para tarifa azul (Alta Tensão).'
    )
    demanda_contratada_fora_ponta = models.FloatField(
        validators=[MinValueValidator(0.0)],
        blank=True,
        null=True,
        help_text='Preencher apenas para tarifa azul (Alta Tensão).'
    )

    fator_potencia = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        blank=True,
        null=True,
        help_text='Fator de potência agora é armazenado aqui em vez do cliente.'
    )

    def clean(self):
        super().clean()

        # Validação das datas
        if self.leitura_atual < self.leitura_anterior:
            raise ValidationError('A leitura atual não pode ser anterior à leitura anterior.')

        if self.vencimento < self.mes:
            raise ValidationError('A data de vencimento não pode ser anterior ao mês de referência.')

        if self.proxima_leitura <= date.today():
            raise ValidationError('A data da próxima leitura deve ser futura.')

        # Validações para Subgrupo BT (Baixa Tensão)
        if self.subgrupo == 'BT':
            if not self.tipo_tarifa_bt:
                raise ValidationError('Tipo de tarifa (Convencional/Branca) é obrigatório para Baixa Tensão.')

            if self.tipo_tarifa_at:
                raise ValidationError('Tipo de tarifa Verde/Azul não é permitido para Baixa Tensão.')

            if self.demanda_contratada_unica or self.demanda_contratada_ponta or self.demanda_contratada_fora_ponta:
                raise ValidationError('Demanda contratada não se aplica a Baixa Tensão.')

        # Validações para Subgrupo AT (Alta Tensão)
        if self.subgrupo == 'AT':
            if not self.tipo_tarifa_at:
                raise ValidationError('Tipo de tarifa (Verde/Azul) é obrigatório para Alta Tensão.')

            if self.tipo_tarifa_bt:
                raise ValidationError('Tipo de tarifa Convencional/Branca não é permitido para Alta Tensão.')

            if self.tipo_tarifa_at == 'Verde':
                if self.demanda_contratada_unica is None:
                    raise ValidationError('Demanda contratada única é obrigatória para tarifa verde.')

            if self.tipo_tarifa_at == 'Azul':
                if self.demanda_contratada_ponta is None or self.demanda_contratada_fora_ponta is None:
                    raise ValidationError('Demanda contratada ponta e fora ponta são obrigatórias para tarifa azul.')

    def __str__(self):
        return f"Conta de Energia - {self.cliente.nome} - {self.mes.strftime('%m/%Y')}"

class ItemFatura(models.Model):
    conta_energia = models.ForeignKey(ContaEnergia, on_delete=models.CASCADE, related_name='itens_fatura')
    descricao = models.CharField(max_length=255)
    quantidade = models.FloatField(validators=[MinValueValidator(0.0)], blank=True, null=True)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    tarifa = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    pis_cofins = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    icms = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.descricao} - Conta ID {self.conta_energia.id}"

class Tributo(models.Model):
    conta_energia = models.ForeignKey(ContaEnergia, on_delete=models.CASCADE, related_name='tributos')
    tipo = models.CharField(max_length=10)  # ICMS, PIS ou COFINS
    base = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    aliquota = models.DecimalField(max_digits=6, decimal_places=4, validators=[MinValueValidator(0)])
    valor = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.tipo} - {self.valor} - Conta {self.conta_energia.id}"

