# Generated by Django 2.1 on 2019-08-15 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_wellmatrix_has_isu'),
    ]

    operations = [
        migrations.CreateModel(
            name='TS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gos_num', models.CharField(db_index=True, max_length=20, unique=True, verbose_name='Гос номер')),
                ('marka', models.CharField(max_length=50, verbose_name='Марка')),
                ('type', models.CharField(max_length=50, verbose_name='Тип')),
                ('total_days', models.IntegerField(default=30, verbose_name='Всего дней')),
                ('in_work', models.IntegerField(default=30, verbose_name='В работу')),
                ('in_rem', models.IntegerField(default=30, verbose_name='В ремонте')),
                ('day_off', models.IntegerField(default=30, verbose_name='Выходной')),
                ('month', models.IntegerField(default=30, verbose_name='Месяц')),
                ('year', models.IntegerField(default=30, verbose_name='Год')),
                ('field', models.CharField(max_length=50, verbose_name='ПСП')),
                ('kip', models.FloatField(default=100, verbose_name='КИП')),
                ('ktg', models.FloatField(default=100, verbose_name='КТГ')),
            ],
            options={
                'verbose_name': 'Транспортное средство',
                'verbose_name_plural': 'Транспортные средства',
            },
        ),
    ]
