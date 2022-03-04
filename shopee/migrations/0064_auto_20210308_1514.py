# Generated by Django 3.1.3 on 2021-03-08 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0063_order_serial_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='serial_number',
        ),
        migrations.AddField(
            model_name='orderpurchase',
            name='serial_number',
            field=models.CharField(blank=True, max_length=70, null=True),
        ),
    ]
