# Generated by Django 2.1 on 2019-08-27 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20190823_1221'),
    ]

    operations = [
        migrations.AddField(
            model_name='gsm',
            name='month',
            field=models.CharField(default=None, max_length=15, verbose_name='Месяц'),
            preserve_default=False,
        ),
    ]
