# Generated by Django 3.1.3 on 2021-01-14 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0030_orderpurchaselineitem'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderpurchase',
            old_name='status',
            new_name='shopee_list_type',
        ),
        migrations.AddField(
            model_name='orderpurchase',
            name='shopee_status',
            field=models.CharField(choices=[('1', 'A Pagar'), ('2', 'A Enviar'), ('3', 'A Receber'), ('4', 'Concluído'), ('5', 'Cancelado')], default='1', max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderpurchaselineitem',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='orderpurchaselineitem',
            name='shopee_model_id',
            field=models.CharField(blank=True, max_length=70, null=True),
        ),
        migrations.AddField(
            model_name='orderpurchaselineitem',
            name='shopee_shop_id',
            field=models.CharField(blank=True, max_length=70, null=True),
        ),
        migrations.AlterField(
            model_name='orderpurchaselineitem',
            name='status',
            field=models.CharField(choices=[('1', 'A Pagar'), ('2', 'A Enviar'), ('3', 'A Receber'), ('4', 'Concluído'), ('5', 'Cancelado')], max_length=1),
        ),
    ]