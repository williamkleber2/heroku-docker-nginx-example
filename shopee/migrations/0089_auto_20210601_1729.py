# Generated by Django 3.1.3 on 2021-06-01 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0088_auto_20210531_1933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usershopee',
            name='captcha_signature',
            field=models.CharField(blank=True, max_length=2500, null=True),
        ),
    ]