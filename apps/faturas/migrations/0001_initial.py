# Generated by Django 5.1.3 on 2024-12-03 21:32

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clientes', '0003_alter_cliente_classificacao_comercial_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContaEnergia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mes', models.DateField(help_text='Data referente ao mês de consumo (use o primeiro dia do mês).')),
                ('vencimento', models.DateField()),
                ('total_pagar', models.DecimalField(decimal_places=2, max_digits=10)),
                ('leitura_anterior', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ('leitura_atual', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ('numero_dias', models.PositiveIntegerField()),
                ('proxima_leitura', models.DateField()),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contas_energia', to='clientes.cliente')),
            ],
        ),
        migrations.CreateModel(
            name='ItensFatura',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consumo_ponta', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ('consumo_fora_ponta', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ('consumo_compensado_fp', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('energia_ativa_injetada_fp', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('demanda_ativa_isenta_icms', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('demanda_ativa', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ('consumo_reativo_excedente_np', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('consumo_reativo_excedente_fp', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('adicional_bandeira', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('conta_energia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens_fatura', to='faturas.contaenergia')),
            ],
        ),
    ]