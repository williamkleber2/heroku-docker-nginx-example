# Generated by Django 3.1.3 on 2021-05-31 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0086_auto_20210420_2127'),
    ]

    operations = [
        migrations.AddField(
            model_name='usershopee',
            name='account_type',
            field=models.CharField(choices=[('G', 'Google'), ('O', 'Other')], default='other', max_length=5),
        ),
        migrations.AlterField(
            model_name='usershopee',
            name='password',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
