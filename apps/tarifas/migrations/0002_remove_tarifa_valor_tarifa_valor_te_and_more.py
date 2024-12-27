# Generated by Django 5.1.3 on 2024-12-27 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tarifas', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tarifa',
            name='valor',
        ),
        migrations.AddField(
            model_name='tarifa',
            name='valor_te',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='tarifa',
            name='valor_tusd',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True),
        ),
    ]