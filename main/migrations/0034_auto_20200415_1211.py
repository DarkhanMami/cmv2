# Generated by Django 2.1 on 2020-04-15 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0033_well_rem_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wellevents',
            name='end',
            field=models.DateTimeField(blank=True, verbose_name='Конец события'),
        ),
    ]
