# Generated by Django 3.1.3 on 2020-12-22 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0004_auto_20201222_0141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productshopee',
            name='item_id',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='productshopee',
            name='model_id',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='productshopee',
            name='shop_id',
            field=models.BigIntegerField(),
        ),
    ]