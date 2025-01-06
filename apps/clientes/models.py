from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from validate_docbr import CNPJ


class Cliente(models.Model):
    ESTADOS_BRASIL = [
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
        ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
        ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'),
    ]

    CLASSIFICACAO_COMERCIAL_CHOICES = [
        ('Residencial', 'Residencial'),
        ('Comercial', 'Comercial'),
        ('Industrial', 'Industrial'),
        ('Rural', 'Rural'),
        ('Poder Público', 'Poder Público'),
    ]

    TIPO_FORNECIMENTO_CHOICES = [
        ('Monofásico', 'Monofásico'),
        ('Bifásico', 'Bifásico'),
        ('Trifásico', 'Trifásico'),
    ]

    nome = models.CharField(max_length=100)
    instalacao = models.CharField(max_length=50, blank=True, null=True)
    cnpj = models.CharField(
        max_length=18,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$',
                message='O CNPJ deve estar no formato 00.000.000/0000-00.'
            )
        ]
    )
    endereco = models.CharField(max_length=200)
    cep = models.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex=r'^\d{5}-\d{3}$',
                message='O CEP deve estar no formato 00000-000.'
            )
        ]
    )
    cidade = models.CharField(max_length=50)
    estado = models.CharField(max_length=2, choices=ESTADOS_BRASIL)
    classificacao_comercial = models.CharField(
        max_length=20,
        choices=CLASSIFICACAO_COMERCIAL_CHOICES
    )
    tipo_fornecimento = models.CharField(
        max_length=20,
        choices=TIPO_FORNECIMENTO_CHOICES
    )
    tensao_nominal_disp = models.FloatField(
        validators=[MinValueValidator(0.0)]
    )

    def clean(self):
        super().clean()
        cnpj_validator = CNPJ()
        if not cnpj_validator.validate(self.cnpj):
            raise ValidationError({'cnpj': 'CNPJ inválido.'})

    def __str__(self):
        return self.nome
