# Generated by Django 3.1.3 on 2021-11-23 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0112_orderlineitem_cancellation_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='usershopee',
            name='banned_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]