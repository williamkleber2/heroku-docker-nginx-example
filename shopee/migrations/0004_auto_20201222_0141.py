# Generated by Django 3.1.3 on 2020-12-22 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0003_auto_20201222_0141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productshopee',
            name='item_id',
            field=models.IntegerField(default=312312321),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='productshopee',
            name='model_id',
            field=models.IntegerField(default=312312),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='productshopee',
            name='shop_id',
            field=models.IntegerField(default=3123123),
            preserve_default=False,
        ),
    ]
