# Generated by Django 2.1 on 2020-09-03 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0036_auto_20200415_1254'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrsDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField(db_index=True, unique=True, verbose_name='Номер')),
            ],
            options={
                'verbose_name': 'Прибор ПРС',
                'verbose_name_plural': 'Приборы ПРС',
            },
        ),
    ]
