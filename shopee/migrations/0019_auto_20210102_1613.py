# Generated by Django 3.1.3 on 2021-01-02 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0018_auto_20210102_1334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderlineitem',
            name='id',
            field=models.CharField(max_length=70, primary_key=True, serialize=False),
        ),
    ]