# Generated by Django 2.1 on 2020-04-15 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0034_auto_20200415_1211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wellevents',
            name='end',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Конец события'),
        ),
    ]
