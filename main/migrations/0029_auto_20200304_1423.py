# Generated by Django 2.1 on 2020-03-04 08:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_auto_20200303_1600'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fieldmatrix',
            name='performance',
        ),
        migrations.RemoveField(
            model_name='sumwellinfield',
            name='performance',
        ),
        migrations.RemoveField(
            model_name='wellmatrix',
            name='active',
        ),
        migrations.RemoveField(
            model_name='wellmatrix',
            name='has_isu',
        ),
        migrations.RemoveField(
            model_name='wellmatrix',
            name='performance',
        ),
    ]
