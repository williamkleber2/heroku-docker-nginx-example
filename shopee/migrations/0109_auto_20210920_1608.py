# Generated by Django 3.1.3 on 2021-09-20 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0108_merge_20210909_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usershopee',
            name='port',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='usershopee',
            name='proxy',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='usershopee',
            name='proxy_login',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='usershopee',
            name='proxy_password',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]