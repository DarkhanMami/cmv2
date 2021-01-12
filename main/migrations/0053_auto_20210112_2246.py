# Generated by Django 2.1 on 2021-01-12 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0052_auto_20210111_2040'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wellmatrix',
            name='tpn',
        ),
        migrations.AddField(
            model_name='well',
            name='pump_depth',
            field=models.FloatField(default=-1, verbose_name='Глубина спуска насоса'),
        ),
        migrations.AddField(
            model_name='well',
            name='tpn',
            field=models.FloatField(default=1, verbose_name='ТПН'),
        ),
        migrations.AddField(
            model_name='wellmatrix',
            name='dyn_level',
            field=models.FloatField(default=1, verbose_name='Дин. уровень'),
        ),
    ]
