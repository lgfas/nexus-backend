from django.db import models


class Distribuidora(models.Model):
    codigo = models.CharField(max_length=14, unique=True)  # Código ANEEL (CNPJ)
    nome = models.CharField(max_length=255)  # Nome da distribuidora
    estado = models.CharField(max_length=2, null=True, blank=True)  # Sigla do estado (SigAgenteAcessante)

    def __str__(self):
        return f"{self.nome} - {self.estado}"


class Tarifa(models.Model):
    distribuidora = models.ForeignKey(Distribuidora, on_delete=models.CASCADE, related_name="tarifas")
    data_geracao_conjunto_dados = models.DateField(null=True, blank=True)  # DatGeracaoConjuntoDados
    dsc_reh = models.TextField(null=True, blank=True)  # DscREH
    data_inicio_vigencia = models.DateField()  # DatInicioVigencia
    data_fim_vigencia = models.DateField(null=True, blank=True)  # DatFimVigencia
    modalidade = models.CharField(max_length=50)  # DscModalidadeTarifaria
    subgrupo = models.CharField(max_length=20)  # DscSubGrupo
    tipo_tarifa = models.CharField(max_length=50)  # DscBaseTarifaria
    valor_tusd = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)  # VlrTUSD
    valor_te = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)  # VlrTE
    dsc_classe = models.TextField(null=True, blank=True)  # DscClasse
    dsc_subclasse = models.TextField(null=True, blank=True)  # DscSubClasse
    dsc_detalhe = models.TextField(null=True, blank=True)  # DscDetalhe
    nom_posto_tarifario = models.TextField(null=True, blank=True)  # NomPostoTarifario
    dsc_unidade_terciaria = models.TextField(null=True, blank=True)  # DscUnidadeTerciaria

    class Meta:
        unique_together = ['distribuidora', 'data_inicio_vigencia', 'modalidade', 'subgrupo', 'tipo_tarifa']

    def __str__(self):
        return f"{self.distribuidora.nome} - {self.modalidade} ({self.tipo_tarifa})"
