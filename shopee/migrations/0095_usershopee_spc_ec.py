# Generated by Django 3.1.3 on 2021-06-04 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0094_auto_20210602_1832'),
    ]

    operations = [
        migrations.AddField(
            model_name='usershopee',
            name='spc_ec',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]