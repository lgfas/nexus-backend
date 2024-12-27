# Generated by Django 5.1.3 on 2024-12-27 13:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Distribuidora',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=10, unique=True)),
                ('nome', models.CharField(max_length=255)),
                ('estado', models.CharField(max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Tarifa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_inicio_vigencia', models.DateField()),
                ('data_fim_vigencia', models.DateField(blank=True, null=True)),
                ('modalidade', models.CharField(max_length=50)),
                ('subgrupo', models.CharField(max_length=20)),
                ('tipo_tarifa', models.CharField(max_length=50)),
                ('valor', models.DecimalField(decimal_places=6, max_digits=10)),
                ('distribuidora', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tarifas', to='tarifas.distribuidora')),
            ],
            options={
                'unique_together': {('distribuidora', 'data_inicio_vigencia', 'modalidade', 'subgrupo', 'tipo_tarifa')},
            },
        ),
    ]