# Generated by Django 3.1.3 on 2021-07-28 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0096_merge_20210716_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='usershop',
            name='automatic_upsell',
            field=models.BooleanField(default=True),
        ),
    ]
