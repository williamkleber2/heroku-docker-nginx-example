# Generated by Django 3.1.6 on 2021-04-15 02:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0083_productvariant_is_processable'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderpurchase',
            name='shopee_order_sn',
            field=models.CharField(blank=True, max_length=70, null=True),
        ),
    ]