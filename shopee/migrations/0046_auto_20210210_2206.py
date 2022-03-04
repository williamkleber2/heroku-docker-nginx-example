# Generated by Django 3.1.3 on 2021-02-10 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0045_order_dropshopee_created_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('AO', 'Aguardando Pedido'), ('AP', 'Aguardando Pagamento'), ('APS', 'Aguardando Pagamento Shopee'), ('AS', 'Aguardando Envio'), ('AF', 'Aguardando Processamento'), ('F', 'Processado'), ('C', 'Cancelado'), ('FO', 'Pedidos Falhadas'), ('DO', 'Pedido Deletado')], max_length=3),
        ),
    ]