# Generated by Django 3.1.3 on 2021-01-14 00:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0027_order_sync_shopee'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='error_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
