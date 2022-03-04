# Generated by Django 3.1.3 on 2021-01-20 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0037_auto_20210118_2141'),
    ]

    operations = [
        migrations.AddField(
            model_name='usershop',
            name='shopify_location_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='usershop',
            name='tracking_url',
            field=models.CharField(default='https://rastreio.ninja/buscar/', max_length=255),
            preserve_default=False,
        ),
    ]