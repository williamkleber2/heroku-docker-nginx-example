# Generated by Django 3.1.3 on 2022-01-17 18:47

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0119_auto_20220114_1813'),
    ]

    operations = [
        migrations.AddField(
            model_name='boleto',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]