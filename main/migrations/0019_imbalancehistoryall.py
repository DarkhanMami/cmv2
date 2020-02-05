# Generated by Django 2.1 on 2020-01-30 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_imbalancehistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImbalanceHistoryAll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(default=0, verbose_name='Число скважен')),
                ('percent', models.FloatField(default=0, verbose_name='Процент от кольичесво скважен')),
                ('timestamp', models.DateTimeField(blank=True, null=True, verbose_name='Дата')),
            ],
            options={
                'verbose_name': 'Неуравновешенность история всех скважен дня',
                'verbose_name_plural': 'Неуравновешенность история всех скважен дней',
            },
        ),
    ]