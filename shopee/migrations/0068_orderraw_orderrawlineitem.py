# Generated by Django 3.1.6 on 2021-04-04 23:58

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0067_orderlineitem_product_variant_id_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderRaw',
            fields=[
                ('id', models.CharField(max_length=70, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(blank=True, max_length=500, null=True)),
                ('neighborhood', models.CharField(blank=True, max_length=500, null=True)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('cpf', models.CharField(blank=True, max_length=255, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=255, null=True)),
                ('client_name', models.CharField(blank=True, max_length=255, null=True)),
                ('client_phone', models.CharField(blank=True, max_length=255, null=True)),
                ('value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subtotal_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_date', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('updated_date', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('user_shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userShopOrdersRaw', to='shopee.usershop')),
            ],
        ),
        migrations.CreateModel(
            name='OrderRawLineItem',
            fields=[
                ('id', models.CharField(max_length=70, primary_key=True, serialize=False)),
                ('quantity', models.IntegerField(default=1)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('product_variant_id_text', models.CharField(blank=True, max_length=70, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orderRawLineItens', to='shopee.orderraw')),
                ('product_variant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orderRawShopifyVariants', to='shopee.productvariant')),
            ],
        ),
    ]
