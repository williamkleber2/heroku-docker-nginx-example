# Generated by Django 3.1.3 on 2021-07-28 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0097_usershop_automatic_upsell'),
    ]

    operations = [
        migrations.AddField(
            model_name='usershop',
            name='notify_order_fulfillment',
            field=models.BooleanField(default=True),
        ),
    ]
