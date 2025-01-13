from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.clientes.models import Cliente
from apps.tarifas.models import Distribuidora


class ContaEnergia(models.Model):
    # Subgrupos
    SUBGRUPO_CHOICES = [
        ('A1', 'A1'), ('A2', 'A2'), ('A3', 'A3'), ('A3a', 'A3a'),
        ('A4', 'A4'), ('A4a', 'A4a'), ('A4b', 'A4b'), ('AS', 'AS'),
        ('B', 'B'), ('B1', 'B1'), ('B2', 'B2'), ('B3', 'B3'), ('B4', 'B4'),
    ]

    # Modalidades associadas
    MODALIDADE_CHOICES = [
        ('Azul', 'Azul'), ('Azul ABRACE CATIVO', 'Azul ABRACE CATIVO'),
        ('Azul ABRACE LIVRE', 'Azul ABRACE LIVRE'), ('Verde', 'Verde'),
        ('Verde ABRACE CATIVO', 'Verde ABRACE CATIVO'), ('Verde ABRACE LIVRE', 'Verde ABRACE LIVRE'),
        ('Branca', 'Branca'), ('Convencional', 'Convencional'),
        ('Convencional ABRACE', 'Convencional ABRACE'),
        ('Convencional pré-pagamento', 'Convencional pré-pagamento'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='contas_energia')
    distribuidora = models.ForeignKey(Distribuidora, on_delete=models.CASCADE, related_name='contas_energia')
    mes = models.DateField(help_text='Data referente ao mês de consumo (use o primeiro dia do mês).')
    vencimento = models.DateField()
    total_pagar = models.DecimalField(max_digits=12, decimal_places=2)

    # Campos ajustados para 'date'
    leitura_anterior = models.DateField(help_text='Data da leitura anterior.')
    leitura_atual = models.DateField(help_text='Data da leitura atual.')
    proxima_leitura = models.DateField(help_text='Data programada para a próxima leitura.')

    numero_dias = models.PositiveIntegerField()

    # Subgrupo e modalidade
    subgrupo = models.CharField(max_length=4, choices=SUBGRUPO_CHOICES)
    modalidade = models.CharField(max_length=50, choices=MODALIDADE_CHOICES)

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

