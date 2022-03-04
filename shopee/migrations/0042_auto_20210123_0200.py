# Generated by Django 3.1.3 on 2021-01-23 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0041_merge_20210123_0200'),
    ]

    operations = [
        migrations.AddField(
            model_name='usershopee',
            name='sms_api_key',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='usershopee',
            name='created_status',
            field=models.CharField(blank=True, choices=[('C', 'Created'), ('BC', 'Being Created'), ('NC', 'Not Created'), ('ENV', 'Email not validated')], max_length=3),
        ),
    ]