# Generated by Django 3.1.3 on 2021-03-05 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0060_userinfo_percentage'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariant',
            name='inventory_item_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
