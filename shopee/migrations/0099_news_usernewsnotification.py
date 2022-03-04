# Generated by Django 3.1.3 on 2021-07-30 20:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shopee', '0098_usershop_notify_order_fulfillment'),
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('brief', models.CharField(max_length=150)),
                ('icon', models.CharField(default='star', max_length=15)),
                ('color', models.CharField(choices=[('primary', 'Azul'), ('secondary', 'Cinza'), ('success', 'Verde'), ('danger', 'Vermelho'), ('warning', 'Amarelo'), ('info', 'Ciano'), ('dark', 'Preto'), ('white', 'Branco')], default='info', max_length=9)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserNewsNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('news', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopee.news')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
