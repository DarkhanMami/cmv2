# Generated by Django 2.1 on 2021-01-14 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0053_auto_20210112_2246'),
    ]

    operations = [
        migrations.AddField(
            model_name='wellmatrix',
            name='electric_cons',
            field=models.FloatField(default=1, verbose_name='Потр. электр.'),
        ),
        migrations.AddField(
            model_name='wellmatrix',
            name='pump_speed',
            field=models.FloatField(default=1, verbose_name='Скорость ст.кач.'),
        ),
        migrations.AlterField(
            model_name='wellmatrix',
            name='filling',
            field=models.FloatField(default=0, verbose_name='Заполн. насоса'),
        ),
        migrations.AlterField(
            model_name='wellmatrix',
            name='fluid_agzu',
            field=models.FloatField(default=0, verbose_name='Жидк. (АГЗУ)'),
        ),
        migrations.AlterField(
            model_name='wellmatrix',
            name='fluid_isu',
            field=models.FloatField(default=0, verbose_name='Жидк. (ИСУ)'),
        ),
        migrations.AlterField(
            model_name='wellmatrix',
            name='p_plast',
            field=models.FloatField(default=0, verbose_name='Давл. (пл)'),
        ),
        migrations.AlterField(
            model_name='wellmatrix',
            name='p_zab',
            field=models.FloatField(default=0, verbose_name='Давл. (заб)'),
        ),
        migrations.AlterField(
            model_name='wellmatrix',
            name='park_fluid',
            field=models.FloatField(default=-1, verbose_name='Парк. жидкость'),
        ),
        migrations.AlterField(
            model_name='wellmatrix',
            name='park_oil',
            field=models.FloatField(default=-1, verbose_name='Парк. нефть'),
        ),
        migrations.AlterField(
            model_name='wellmatrix',
            name='tbd_fluid',
            field=models.FloatField(default=-1, verbose_name='ТБД жидк.'),
        ),
        migrations.AlterField(
            model_name='wellmatrix',
            name='teh_rej_fluid',
            field=models.FloatField(default=0, verbose_name='Т/р жидкости'),
        ),
        migrations.AlterField(
            model_name='wellmatrix',
            name='teh_rej_oil',
            field=models.FloatField(default=0, verbose_name='Т/р нефти'),
        ),
        migrations.AlterField(
            model_name='wellmatrix',
            name='teh_rej_water',
            field=models.FloatField(default=0, verbose_name='Обводн.'),
        ),
    ]
