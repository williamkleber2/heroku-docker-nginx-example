# Generated by Django 3.1.3 on 2021-01-17 15:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0035_auto_20210116_2317'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderpurchaselineitem',
            name='shopee_order_id',
        ),
    ]