# Generated by Django 3.1.3 on 2020-12-26 04:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0005_auto_20201222_0200'),
    ]

    operations = [
        migrations.AddField(
            model_name='usershopee',
            name='spc_f',
            field=models.CharField(default=22, max_length=255),
            preserve_default=False,
        ),
    ]