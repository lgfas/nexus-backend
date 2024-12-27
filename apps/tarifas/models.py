from django.db import models


class Distribuidora(models.Model):
    codigo = models.CharField(max_length=14, unique=True)  # Código ANEEL (CNPJ)
    nome = models.CharField(max_length=255)  # Nome da distribuidora
    estado = models.CharField(max_length=2)  # Sigla do estado

    def __str__(self):
        return f"{self.nome} - {self.estado}"


class Tarifa(models.Model):
    distribuidora = models.ForeignKey(Distribuidora, on_delete=models.CASCADE, related_name="tarifas")
    data_inicio_vigencia = models.DateField()
    data_fim_vigencia = models.DateField(null=True, blank=True)
    modalidade = models.CharField(max_length=50)
    subgrupo = models.CharField(max_length=20)
    tipo_tarifa = models.CharField(max_length=50)
    valor_tusd = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    valor_te = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)

    class Meta:
        unique_together = ['distribuidora', 'data_inicio_vigencia', 'modalidade', 'subgrupo', 'tipo_tarifa']

    def __str__(self):
        return f"{self.distribuidora.nome} - {self.modalidade} ({self.tipo_tarifa})"
