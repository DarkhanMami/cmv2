# Generated by Django 2.1 on 2020-09-24 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0039_recommendation'),
    ]

    operations = [
        migrations.AddField(
            model_name='recommendation',
            name='kpn',
            field=models.FloatField(default=1, verbose_name='Коэф. подачи насоса'),
        ),
    ]
