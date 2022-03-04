# Generated by Django 3.1.3 on 2022-01-04 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopee', '0116_merge_20220103_1813'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='send_mail',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='report',
            name='url',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='user_shop',
            field=models.ForeignKey(default='', on_delete=models.deletion.CASCADE, to='shopee.usershop'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='report',
            name='status',
            field=models.CharField(choices=[('finished', 'Finished'), ('pending', 'Pending'), ('error', 'Error')], default='pending', max_length=100),
        ),
    ]