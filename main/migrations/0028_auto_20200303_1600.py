# Generated by Django 2.1 on 2020-03-03 10:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_auto_20200303_1549'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fieldmatrix',
            options={'verbose_name': 'Баланс месторождении', 'verbose_name_plural': 'Баланс месторождений'},
        ),
        migrations.AlterModelOptions(
            name='sumwellinfield',
            options={'verbose_name': 'Баланс месторождении (ИСУ)', 'verbose_name_plural': 'Баланс месторождений (ИСУ)'},
        ),
    ]
