# Generated by Django 2.1 on 2019-11-20 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_imbalance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imbalance',
            name='timestamp',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата опроса'),
        ),
    ]
