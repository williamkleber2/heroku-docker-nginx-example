# Generated by Django 3.1.3 on 2021-01-16 20:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0032_auto_20210115_2146'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderpurchase',
            old_name='shopee_status',
            new_name='status',
        ),
        migrations.RenameField(
            model_name='orderpurchaselineitem',
            old_name='shopee_status',
            new_name='status',
        ),
    ]