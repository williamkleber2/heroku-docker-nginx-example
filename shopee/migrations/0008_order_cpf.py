# Generated by Django 3.1.3 on 2020-12-27 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0007_auto_20201226_2108'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cpf',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]