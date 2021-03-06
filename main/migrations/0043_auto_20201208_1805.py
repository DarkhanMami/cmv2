# Generated by Django 2.1 on 2020-12-08 12:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0042_auto_20201008_1916'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')),
            ],
            options={
                'verbose_name': 'Рассылка',
                'verbose_name_plural': 'Рассылки',
            },
        ),
        migrations.CreateModel(
            name='MailSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Снижение добычи', 'Снижение добычи'), ('Ухудшение работы скважины', 'Ухудшение работы скважины'), ('Сводка по ИСУ', 'Сводка по ИСУ'), ('Прочее', 'Прочее')], default='Прочее', max_length=30, verbose_name='Тип')),
                ('body', models.CharField(max_length=600, verbose_name='Текст')),
                ('freq', models.IntegerField(default=0, verbose_name='Периодичность')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mail_fields', to='main.Field')),
            ],
            options={
                'verbose_name': 'Настройка рассылки',
                'verbose_name_plural': 'Настройки рассылки',
            },
        ),
        migrations.CreateModel(
            name='MailUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=50, verbose_name='Значение')),
                ('name', models.CharField(max_length=50, verbose_name='Имя')),
                ('mail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mail_sets', to='main.MailSettings')),
            ],
            options={
                'verbose_name': 'Пользователь рассылки',
                'verbose_name_plural': 'Пользователи рассылки',
            },
        ),
        migrations.AddField(
            model_name='mailhistory',
            name='mail',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mails', to='main.MailSettings', verbose_name='Рассылка'),
        ),
    ]
