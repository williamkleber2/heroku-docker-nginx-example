# Generated by Django 3.1.3 on 2021-06-02 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0090_auto_20210602_1655'),
    ]

    operations = [
        migrations.AddField(
            model_name='usershopee',
            name='identity_token',
            field=models.CharField(blank=True, max_length=2500, null=True),
        ),
    ]
