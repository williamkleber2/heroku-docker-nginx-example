# Generated by Django 3.1.3 on 2021-02-10 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0047_order_dropshopee_deleted_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='usershopee',
            name='creation_request_date',
            field=models.DateTimeField(null=True),
        ),
    ]
