# Generated by Django 3.1.3 on 2021-08-24 23:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0105_merge_20210824_1953'),
    ]

    operations = [
        migrations.AddField(
            model_name='userbillingdata',
            name='address_number',
            field=models.CharField(max_length=6),
        ),
    ]
