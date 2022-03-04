# Generated by Django 3.1.3 on 2021-02-25 05:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0055_auto_20210223_0231'),
    ]

    operations = [
        migrations.CreateModel(
            name='PercentagePay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('paid', 'Pago'), ('unpaid', 'Não Pago'), ('past_due', 'Pagamento atrasado')], max_length=10)),
                ('retry', models.IntegerField(default=3)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('payment_intent_id', models.CharField(blank=True, max_length=70, null=True, unique=True)),
                ('error_message', models.CharField(blank=True, max_length=255, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopee.customer')),
            ],
        ),
    ]