# Generated by Django 3.1.3 on 2021-01-08 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0023_auto_20210107_2259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvariant',
            name='sku',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
