# Generated by Django 3.1.6 on 2021-06-05 21:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0086_auto_20210420_2127'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='hasChild',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='parentOrder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='childOrders', to='shopee.order'),
        ),
    ]
