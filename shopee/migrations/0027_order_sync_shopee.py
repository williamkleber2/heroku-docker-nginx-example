# Generated by Django 3.1.3 on 2021-01-12 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0026_auto_20210110_0026'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='sync_shopee',
            field=models.BooleanField(default=False),
        ),
    ]