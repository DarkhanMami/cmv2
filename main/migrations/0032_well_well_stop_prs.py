# Generated by Django 2.1 on 2020-04-11 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_auto_20200411_1907'),
    ]

    operations = [
        migrations.AddField(
            model_name='well',
            name='well_stop_prs',
            field=models.FloatField(default=0, verbose_name='Остановы (ПРС)'),
        ),
    ]