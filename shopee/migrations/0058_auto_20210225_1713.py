# Generated by Django 3.1.3 on 2021-02-25 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0057_order_percentage_pay'),
    ]

    operations = [
        migrations.AlterField(
            model_name='percentagepay',
            name='status',
            field=models.CharField(choices=[('paid', 'Pago'), ('unpaid', 'Não Pago'), ('past_due', 'Pagamento atrasado'), ('refunded', 'Reembolsado')], max_length=10),
        ),
    ]
