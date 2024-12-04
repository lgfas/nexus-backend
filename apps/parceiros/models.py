from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class Parceiro(models.Model):
    TIPO_PARCEIRO_CHOICES = [
        ('Fornecedor', 'Fornecedor'),
        ('Distribuidor', 'Distribuidor'),
        ('Varejista', 'Varejista'),
        ('Outros', 'Outros'),
    ]

    nome = models.CharField(max_length=100)
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
    estado = models.CharField(max_length=2, choices=[
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AP', 'Amapá'),
        ('AM', 'Amazonas'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MT', 'Mato Grosso'),
        ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PR', 'Paraná'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'),
        ('SE', 'Sergipe'),
        ('TO', 'Tocantins'),
    ])
    tipo = models.CharField(max_length=20, choices=TIPO_PARCEIRO_CHOICES)
    telefone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$',
                message='Telefone inválido. Formato esperado: (00) 0000-0000 ou (00) 00000-0000.'
            )
        ]
    )
    email = models.EmailField(unique=True)

    def clean(self):
        super().clean()
        # Validação adicional do CNPJ pode ser implementada aqui usando uma biblioteca
        # como validate-docbr para validar os dígitos verificadores do CNPJ
        from validate_docbr import CNPJ
        cnpj_validator = CNPJ()
        if not cnpj_validator.validate(self.cnpj):
            raise ValidationError({'cnpj': 'CNPJ inválido.'})

    def __str__(self):
        return self.nome

