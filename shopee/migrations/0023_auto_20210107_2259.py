# Generated by Django 3.1.3 on 2021-01-07 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0022_usershopee_deactivate_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='street_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]