# Generated by Django 3.0.8 on 2021-01-07 00:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0021_usershop_working_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='usershopee',
            name='deactivate_status',
            field=models.CharField(blank=True, choices=[('IL', 'Login incorreto'), ('IP', 'Proxy incorreta'), ('IT', 'Token inválido'), ('TE', 'Erro ao finalizar transação'), ('M', 'Manual')], max_length=2, null=True),
        ),
    ]
