# Generated by Django 3.1.3 on 2021-01-22 10:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0038_auto_20210119_2109'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usershopee',
            options={'permissions': [('create_user_on_shopee', 'Can create a user directly on shopee')]},
        ),
        migrations.AlterField(
            model_name='usershopee',
            name='phone',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='usershopee',
            name='user_shop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shopeeUsers', to='shopee.usershop'),
        ),
    ]
