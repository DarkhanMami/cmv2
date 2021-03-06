# Generated by Django 2.1 on 2020-02-01 14:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_imbalancehistoryall'),
    ]

    operations = [
        migrations.CreateModel(
            name='SumWellInField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filling', models.FloatField(default=0, verbose_name='Заполнение насоса')),
                ('fluid_agzu', models.FloatField(default=0, verbose_name='Жидкость (АГЗУ)')),
                ('fluid_isu', models.FloatField(default=0, verbose_name='Жидкость (ИСУ)')),
                ('shortage_isu', models.FloatField(default=0, verbose_name='Недобор (ИСУ)')),
                ('shortage_prs', models.FloatField(default=0, verbose_name='Недобор (ПРС)')),
                ('shortage_wait', models.FloatField(default=0, verbose_name='Недобор (Ожид.тех)')),
                ('teh_rej_fluid', models.FloatField(default=0, verbose_name='Техрежим жидкости')),
                ('teh_rej_oil', models.FloatField(default=0, verbose_name='Техрежим нефти')),
                ('teh_rej_water', models.FloatField(default=0, verbose_name='Обводненность')),
                ('brigade_num', models.IntegerField(default=0, verbose_name='Номер бригады')),
                ('ts_num', models.CharField(blank=True, default='', max_length=20, verbose_name='Номер ТС')),
                ('well_stop', models.FloatField(default=0, verbose_name='Остановы')),
                ('oil_loss', models.FloatField(default=0, verbose_name='Потери')),
                ('active', models.BooleanField(default=False, verbose_name='Активный')),
                ('performance', models.FloatField(default=100, verbose_name='Производительность')),
                ('has_isu', models.BooleanField(default=False, verbose_name='Оснащен ИСУ')),
                ('timestamp', models.DateField(blank=True, null=True, verbose_name='Дата')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='well_in_fields', to='main.Field')),
            ],
        ),
        migrations.RemoveField(
            model_name='well',
            name='teh_rej_fluid',
        ),
        migrations.RemoveField(
            model_name='well',
            name='teh_rej_oil',
        ),
        migrations.RemoveField(
            model_name='well',
            name='teh_rej_water',
        ),
        migrations.AddField(
            model_name='wellmatrix',
            name='teh_rej_fluid',
            field=models.FloatField(default=0, verbose_name='Техрежим жидкости'),
        ),
        migrations.AddField(
            model_name='wellmatrix',
            name='teh_rej_oil',
            field=models.FloatField(default=0, verbose_name='Техрежим нефти'),
        ),
        migrations.AddField(
            model_name='wellmatrix',
            name='teh_rej_water',
            field=models.FloatField(default=0, verbose_name='Обводненность'),
        ),
        migrations.AddField(
            model_name='wellmatrix',
            name='timestamp',
            field=models.DateField(blank=True, null=True, verbose_name='Дата'),
        ),
    ]
