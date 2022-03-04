# Generated by Django 3.1.3 on 2021-08-19 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0104_merge_20210818_0142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usershopee',
            name='deactivate_status',
            field=models.CharField(blank=True, choices=[('IL', 'Login incorreto'), ('IP', 'Proxy incorreta'), ('IT', 'Token inválido'), ('TE', 'Erro ao finalizar transação'), ('M', 'Manual'), ('BA', 'Conta banida'), ('EL', 'Login expirou'), ('FSL', 'Limite de Frete Grátis'), ('EL', 'Login Expirado')], default='', max_length=3),
        ),
    ]
