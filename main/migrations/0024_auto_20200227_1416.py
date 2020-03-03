# Generated by Django 2.1 on 2020-02-27 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_wellevents'),
    ]

    operations = [
        migrations.AddField(
            model_name='well',
            name='tbd_id',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='tbd_id'),
        ),
        migrations.AlterField(
            model_name='well',
            name='well_id',
            field=models.IntegerField(default=0, verbose_name='sdmo_id'),
        ),
    ]