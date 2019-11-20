# import uuid
#
# from django.db import models
# from django.contrib.auth.models import (
#     BaseUserManager, AbstractBaseUser
# )
# from django.contrib.postgres.fields import ArrayField
# from django.utils.translation import gettext as _
# from tinymce.models import HTMLField
# from main.models import *
#
# def uploaded_filename(instance, filename):
#     """
#     Scramble / uglify the filename of the uploaded file, but keep the files extension (e.g., .jpg or .png)
#     :param instance:
#     :param filename:
#     :return:
#     """
#     extension = filename.split(".")[-1]
#     return "{}/{}.{}".format(instance.pk, uuid.uuid4(), extension)
#
#
# class Field(models.Model):
#     name = models.CharField(max_length=255, blank=False, null=False, unique=True, db_index=True,
#                             verbose_name=_('Название'))
#
#     class Meta:
#         verbose_name = _("Месторождение")
#         verbose_name_plural = _("Месторождения")
#
#     def __str__(self):
#         return self.name
#
#
# class Well(models.Model):
#     name = models.CharField(max_length=255, blank=False, null=False, unique=True, db_index=True,
#                             verbose_name=_('Название'))
#     field = models.ForeignKey(Field, blank=False, null=False, on_delete=models.CASCADE, related_name='fields')
#     teh_rej_fluid = models.FloatField(default=0, verbose_name=_('Техрежим жидкости'))
#     teh_rej_oil = models.FloatField(default=0, verbose_name=_('Техрежим нефти'))
#     teh_rej_water = models.FloatField(default=0, verbose_name=_('Обводненность'))
#
#     SGN = "ШГН"
#     EVN = "ЭВН"
#     PRODUCTION_TYPES = (
#         (SGN, _('ШГН')),
#         (EVN, _('ЭВН')),
#     )
#
#     production_type = models.CharField(choices=PRODUCTION_TYPES, default=SGN, max_length=100,
#                                        verbose_name=_("Технология добычи"))
#
#     class Meta:
#         verbose_name = _("Скважина")
#         verbose_name_plural = _("Скважины")
#
#     def __str__(self):
#         return self.name
#
#
# class WellMatrix(models.Model):
#     well = models.ForeignKey(Well, blank=False, null=False, on_delete=models.CASCADE, related_name='wells')
#
#     filling = models.FloatField(default=0, verbose_name=_('Заполнение насоса'))
#     fluid_agzu = models.FloatField(default=0, verbose_name=_('Жидкость (АГЗУ)'))
#     fluid_isu = models.FloatField(default=0, verbose_name=_('Жидкость (ИСУ)'))
#
#     shortage_isu = models.FloatField(default=0, verbose_name=_('Недобор (ИСУ)'))
#     shortage_prs = models.FloatField(default=0, verbose_name=_('Недобор (ПРС)'))
#     shortage_wait = models.FloatField(default=0, verbose_name=_('Недобор (Ожид.тех)'))
#
#     brigade_num = models.IntegerField(default=0, verbose_name=_('Номер бригады'))
#     ts_num = models.CharField(max_length=20, blank=True, default="", verbose_name=_('Номер ТС'))
#
#     well_stop = models.FloatField(default=0, verbose_name=_('Остановы'))
#     oil_loss = models.FloatField(default=0, verbose_name=_('Потери'))
#
#     active = models.BooleanField(default=False, verbose_name=_('Активный'))
#     performance = models.FloatField(default=100, verbose_name=_('Производительность'))
#     has_isu = models.BooleanField(default=False, verbose_name=_('Оснащен ИСУ'))
#
#     class Meta:
#         verbose_name = _("Матрица")
#         verbose_name_plural = _("Матрица")
#
#
# class Depression(models.Model):
#     well = models.ForeignKey(Well, blank=False, null=False, on_delete=models.CASCADE, related_name='depression_wells')
#
#     densityPL = models.FloatField(default=0, verbose_name=_('Давление (Пласт)'))
#     densityZB = models.FloatField(default=0, verbose_name=_('Давление (Забой)'))
#     densityDiff = models.FloatField(default=0, verbose_name=_('Разница'))
#     fluid_av = models.FloatField(default=0, verbose_name=_('Жидкость (ср.)'))
#
#     timestamp = models.DateField(blank=False, verbose_name=_('Дата'))
#
#     class Meta:
#         verbose_name = _("Подбор депрессии")
#         verbose_name_plural = _("Подбор депрессий")
#
#
# class FieldBalance(models.Model):
#     field = models.ForeignKey(Field, blank=False, null=False, on_delete=models.CASCADE, related_name='bal_fields')
#     transport_balance = models.FloatField(default=0, db_index=True, verbose_name=_('Автомобильные весы (жидкость)'))
#     ansagan_balance = models.FloatField(default=0, db_index=True, verbose_name=_('Весы по Ансаган (жидкость)'))
#     transport_brutto = models.FloatField(default=0, db_index=True, verbose_name=_('Автомобильные весы (брутто)'))
#     ansagan_brutto = models.FloatField(default=0, db_index=True, verbose_name=_('Весы по Ансаган (брутто)'))
#     transport_netto = models.FloatField(default=0, db_index=True, verbose_name=_('Автомобильные весы (нетто)'))
#     ansagan_netto = models.FloatField(default=0, db_index=True, verbose_name=_('Весы по Ансаган (нетто)'))
#     transport_density = models.FloatField(default=0, db_index=True, verbose_name=_('Автомобильные весы (плотность)'))
#     ansagan_density = models.FloatField(default=0, db_index=True, verbose_name=_('Весы по Ансаган (плотность)'))
#
#     agzu_fluid = models.FloatField(default=0, db_index=True, verbose_name=_('Замер жидкости по скважинам'))
#     agzu_oil = models.FloatField(default=0, db_index=True, verbose_name=_('Замер нефти по скважинам'))
#     teh_rej_fluid = models.FloatField(default=0, db_index=True, verbose_name=_('Замер по Тех. жидкости'))
#     teh_rej_oil = models.FloatField(default=0, db_index=True, verbose_name=_('Замер по Тех. нефти'))
#
#     timestamp = models.DateField(blank=False, verbose_name=_('Дата замера'))
#
#     class Meta:
#         verbose_name = _("Баланс по месторождению")
#         verbose_name_plural = _("Баланс по месторождениям")
#
#
# class TS(models.Model):
#     gos_num = models.CharField(max_length=20, blank=False, null=False, verbose_name=_('Гос номер'))
#     marka = models.CharField(max_length=50, verbose_name=_('Марка'))
#     type = models.CharField(max_length=50, verbose_name=_('Тип'))
#     total_days = models.IntegerField(default=30, verbose_name=_('Всего дней'))
#     in_work = models.IntegerField(default=30, verbose_name=_('В работу'))
#     in_rem = models.IntegerField(default=30, verbose_name=_('В ремонте'))
#     day_off = models.IntegerField(default=30, verbose_name=_('Выходной'))
#     month = models.IntegerField(default=30, verbose_name=_('Месяц'))
#     year = models.IntegerField(default=2019, verbose_name=_('Год'))
#     field = models.CharField(max_length=50, verbose_name=_('ПСП'))
#     kip = models.FloatField(default=100, verbose_name=_('КИП'))
#     ktg = models.FloatField(default=100, verbose_name=_('КТГ'))
#
#     class Meta:
#         verbose_name = _("Транспортное средство")
#         verbose_name_plural = _("Транспортные средства")
#
#     def __str__(self):
#         return self.gos_num
#
#
# class GSM(models.Model):
#     gos_num = models.CharField(max_length=50, blank=False, null=False, verbose_name=_('Гос номер'))
#     type = models.CharField(max_length=100, verbose_name=_('Тип'))
#     year = models.IntegerField(default=2019, verbose_name=_('Год'))
#     month = models.IntegerField(default=-1, verbose_name=_('Месяц'))
#     field = models.CharField(max_length=30, verbose_name=_('ПСП'))
#     gsm_type = models.CharField(max_length=50, verbose_name=_('Тип ГСМ'))
#     sum = models.FloatField(default=0, verbose_name=_('Сумма во ВВ'))
#     quantity = models.FloatField(default=0, verbose_name=_('Количество'))
#
#     class Meta:
#         verbose_name = _("ГСМ")
#         verbose_name_plural = _("ГСМ")
#
#     def __str__(self):
#         return self.gos_num
#
#
# class ProdProfile(models.Model):
#     well = models.ForeignKey(Well, blank=False, null=False, on_delete=models.CASCADE, related_name='prof_wells')
#     well_pair = models.IntegerField(default=-1, verbose_name=_('Пара'))
#     pre_fluid = models.FloatField(default=0, verbose_name=_('Жидкость (До)'))
#     post_fluid = models.FloatField(default=0, verbose_name=_('Жидкость (После)'))
#     pre_oil = models.FloatField(default=0, verbose_name=_('Нефть (До)'))
#     post_oil = models.FloatField(default=0, verbose_name=_('Нефть (После)'))
#     pre_obv = models.FloatField(default=0, verbose_name=_('Обводненность (До)'))
#     post_obv = models.FloatField(default=0, verbose_name=_('Обводненность (После)'))
#     effect = models.FloatField(default=0, verbose_name=_('Эффект (нефть)'))
#
#     class Meta:
#         verbose_name = _("Профиль добычи")
#         verbose_name_plural = _("Профиль добычи")
#
#
# class Dynamogram(models.Model):
#     well = models.ForeignKey(Well, blank=False, null=False, on_delete=models.CASCADE, related_name='dyn_wells')
#     x = ArrayField(models.FloatField(), blank=True)
#     y = ArrayField(models.FloatField(), blank=True)
#     timestamp = models.DateTimeField(blank=False, verbose_name=_('Время замера'))
#
#     class Meta:
#         verbose_name = _("Динамограмма скважины")
#         verbose_name_plural = _("Динамограммы скважин")
#
#
# #################--------cm2_first_db_schemas----------##################################################################################################################################################
#
#
# class GpsUsers(models.Model):
#     name = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Ф.И.О'))
#     oil_field = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Месторождение'))
#     ngdu_code = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Код НГДУ'))
#
#     class Meta:
#         verbose_name = _("GPS пользователь")
#         verbose_name_plural = _("GPS пользователи")
#
#     def __str__(self):
#         return self.name
#
#
# class GpsTracks(models.Model):
#     user = models.ForeignKey(GpsUsers, blank=False, null=False, on_delete=models.CASCADE, related_name='gps_user')
#     time = models.IntegerField(default=0, verbose_name=_('Время'))
#     latitude = models.FloatField(default=0, verbose_name=_('Широта'))
#     longitude = models.FloatField(default=0, verbose_name=_('Долгота'))
#     work_id = models.IntegerField(default=0, verbose_name=_('Работа'))
#     well_id = models.IntegerField(default=0, verbose_name=_('Скважина'))
#
#     class Meta:
#         verbose_name = _("GPS трэк")
#         verbose_name_plural = _("GPS трэки")
#
#     def __str__(self):
#         return self.name
#
#
# class GpsTracksArchive(models.Model):
#     user = models.ForeignKey(GpsUsers, blank=False, null=False, on_delete=models.CASCADE, related_name='gps_user_acrh')
#     time = models.IntegerField(default=0, verbose_name=_('Время'))
#     latitude = models.FloatField(default=0, verbose_name=_('Широта'))
#     longitude = models.FloatField(default=0, verbose_name=_('Долгота'))
#     work_id = models.IntegerField(default=0, verbose_name=_('Работа'))
#
#     class Meta:
#         verbose_name = _("GPS трэк")
#         verbose_name_plural = _("GPS трэки")
#
#     def __str__(self):
#         return self.name
#
#
# class GpsWells(models.Model):
#     oil_field = models.CharField(max_length=25, blank=True, default="", verbose_name=_('Нефть'))
#     number = models.IntegerField(default=0, verbose_name=_('Номер'))
#     name = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Название'))
#     latitude = models.FloatField(default=0, verbose_name=_('Широта'))
#     longitude = models.FloatField(default=0, verbose_name=_('Долгота'))
#     gps_type = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Тип'))
#     gps_map = models.IntegerField(default=0, verbose_name=_('Карта'))
#     from_mobile = models.IntegerField(default=0, verbose_name=_('Из мобильного'))
#
#     class Meta:
#         verbose_name = _("GPS скважина")
#         verbose_name_plural = _("GPS скважины")
#
#     def __str__(self):
#         return self.name
#
#
# class Gps_works(models.Model):
#     code = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Код'))
#     name = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Название'))
#
#     class Meta:
#         verbose_name = _("GPS пользователь")
#         verbose_name_plural = _("GPS пользователи")
#
#     def __str__(self):
#         return self.name
#
#
# class N_2hour(models.Model):
#     oil_filed = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Нефть'))
#     time = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Время'))
#     current_debit = models.FloatField(default=0, verbose_name=_('Текущий дебит'))
#     debit_last_day = models.FloatField(default=0, verbose_name=_('Дебит прошлого дня'))
#     tech_rezh = models.FloatField(default=0, verbose_name=_('Тех/режим'))
#     current_debit_nak = models.FloatField(default=0, verbose_name=_('Текущий дебит с накоплением'))
#     debit_last_day_nak = models.FloatField(default=0, verbose_name=_('Дебит прошлого дня с накоплением'))
#     tech_rezh_nak = models.FloatField(default=0, verbose_name=_('Тех/режим с накоплением'))
#     n_current_debit = models.FloatField(default=0, verbose_name=_('Нефть текущий дебит'))
#     n_tech_rezh = models.FloatField(default=0, verbose_name=_('Нефть тех/режим'))
#     n_current_debit_nak = models.FloatField(default=0, verbose_name=_('Нефть текущий дебит с накоплением'))
#     n_debit_last_day_nak = models.FloatField(default=0, verbose_name=_('Нефть дебит прошлого дня с накоплением'))
#     n_tech_rezh_nak = models.FloatField(default=0, verbose_name=_('Нефть тех/режим с накоплением'))
#     tin = models.IntegerField(default=0, verbose_name=_('Тин'))
#     ngdu = models.CharField(max_length=255, blank=True, default="", verbose_name=_('НГДУ'))
#     oil_out = models.FloatField(default=0, verbose_name=_('Нефть сдача'))
#     oil_out_nak = models.FloatField(default=0, verbose_name=_('Нефть сдача с накоплением'))
#     wat_out = models.FloatField(default=0, verbose_name=_('Слив воды'))
#     wat_out_nak = models.FloatField(default=0, verbose_name=_('Слив воды с накоплением'))
#
#     class Meta:
#         verbose_name = _("2-часовой показатель")
#         verbose_name_plural = _("2-часовые показатели")
#
#     def __str__(self):
#         return self.name
#
#
# class N_2hour_archive(models.Model):
#     oil_filed = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Нефть'))
#     time = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Время'))
#     current_debit = models.FloatField(default=0, verbose_name=_('Текущий дебит'))
#     debit_last_day = models.FloatField(default=0, verbose_name=_('Дебит прошлого дня'))
#     tech_rezh = models.FloatField(default=0, verbose_name=_('Тех/режим'))
#     current_debit_nak = models.FloatField(default=0, verbose_name=_('Текущий дебит с накоплением'))
#     debit_last_day_nak = models.FloatField(default=0, verbose_name=_('Дебит прошлого дня с накоплением'))
#     tech_rezh_nak = models.FloatField(default=0, verbose_name=_('Тех/режим с накоплением'))
#     n_current_debit = models.FloatField(default=0, verbose_name=_('Нефть текущий дебит'))
#     n_tech_rezh = models.FloatField(default=0, verbose_name=_('Нефть тех/режим'))
#     n_current_debit_nak = models.FloatField(default=0, verbose_name=_('Нефть текущий дебит с накоплением'))
#     n_debit_last_day_nak = models.FloatField(default=0, verbose_name=_('Нефть дебит прошлого дня с накоплением'))
#     n_tech_rezh_nak = models.FloatField(default=0, verbose_name=_('Нефть тех/режим с накоплением'))
#     tin = models.IntegerField(default=0, verbose_name=_('Тин'))
#     ngdu = models.CharField(max_length=255, blank=True, default="", verbose_name=_('НГДУ'))
#     oil_out = models.FloatField(default=0, verbose_name=_('Нефть сдача'))
#     oil_out_nak = models.FloatField(default=0, verbose_name=_('Нефть сдача с накоплением'))
#     wat_out = models.FloatField(default=0, verbose_name=_('Слив воды'))
#     wat_out_nak = models.FloatField(default=0, verbose_name=_('Слив воды с накоплением'))
#
#     class Meta:
#         verbose_name = _("2-часовой показатель (архив)")
#         verbose_name_plural = _("2-часовые показатели (архив)")
#
#     def __str__(self):
#         return self.name
#
#
# class N_cppn(models.Model):
#     tag = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Тэг'))
#     value = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Значение'))
#
#     class Meta:
#         verbose_name = _("ЦППН")
#         verbose_name_plural = _("ЦППН")
#
#     def __str__(self):
#         return self.name
#
#
# class N_danfoss(models.Model):
#     oil_field = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Нефть'))
#     well = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Скважина'))
#     date = models.DateField(blank=False, verbose_name=_('Дата'))
#     no_work_hours = models.FloatField(default=0, verbose_name=_('Время не работы'))
#     idle_hours = models.FloatField(default=0, verbose_name=_('Часы простоя'))
#     oil_loss = models.FloatField(default=0, verbose_name=_('Потери нефти'))
#
#     class Meta:
#         verbose_name = _("Данфосс")
#         verbose_name_plural = _("Данфосс")
#
#     def __str__(self):
#         return self.name
#
#
# class N_events(models.Model):
#     status = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Статус'))
#     criticality = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Критичность'))
#     event = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Проишествие'))
#     closed = models.DateTimeField(blank=False, verbose_name=_('Дата/Время'))
#     _object = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Объект'))
#     oil_field = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Нефть'))
#     well = models.CharField(max_length=45, blank=True, default="", verbose_name=_('Скважина'))
#     agzu = models.CharField(max_length=45, blank=True, default="", verbose_name=_('АГЗУ'))
#     otvod = models.CharField(max_length=45, blank=True, default="", verbose_name=_('Отвод'))
#     user_name = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Пользователь'))
#     user_email = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Почта пользователя'))
#     opened = models.DateTimeField(blank=False, verbose_name=_('Время'))
#     delta = models.FloatField(default=0, verbose_name=_('Дельта'))
#     comment = models.CharField(max_length=300, blank=True, default="", verbose_name=_('Комментарий'))
#
#     class Meta:
#         verbose_name = _("Проишествие")
#         verbose_name_plural = _("Проишествия")
#
#     def __str__(self):
#         return self.name
#
#
# class N_expenses(models.Model):
#     _type = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Тип'))
#     operation = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Работа'))
#     _sum = models.FloatField(default=0, verbose_name=_('Сумма'))
#
#     class Meta:
#         verbose_name = _("Затрата")
#         verbose_name_plural = _("Затраты")
#
#     def __str__(self):
#         return self.name
#
#
# class N_kes(models.Model):
#     oil_field = models.CharField(max_length=20, blank=True, default="", verbose_name=_('Нефть'))
#     date = models.DateField(blank=False, verbose_name=_('Дата'))
#     kes = models.FloatField(default=0, verbose_name=_('КЭС'))
#     no_work_hours = models.FloatField(default=0, verbose_name=_('Время не работы'))
#
#     class Meta:
#         verbose_name = _("КЭС")
#         verbose_name_plural = _("КЭС")
#
#     def __str__(self):
#         return self.name
#
#
# class N_last10(models.Model):
#     oil_filed = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Нефть'))
#     well = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Скважина'))
#     start_date = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Дата начало'))
#     end_date = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Дата конец'))
#     _type = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Тип'))
#     work = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Работа'))
#
#     # foreign_id = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Инос ключ')) ???????????????????????/
#
#     class Meta:
#         verbose_name = _("Последние 10 показателей")
#         verbose_name_plural = _("Последние 10 показателей")
#
#     def __str__(self):
#         return self.name
#
#
# class N_last_ten(models.Model):
#     ngdu = models.CharField(max_length=255, blank=True, default="", verbose_name=_('НГДУ'))
#     oil_field = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Нефть'))
#     well = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Скважина'))
#     _type = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Тип'))
#     tr_fluid = models.FloatField(default=0, verbose_name=_('Тех/режим жидкость'))
#     tr_obv = models.FloatField(default=0, verbose_name=_('Тех/режим обводненность'))
#     tr_oil = models.FloatField(default=0, verbose_name=_('Тех/режим нефть'))
#     before_fluid = models.FloatField(default=0, verbose_name=_('Жидкость (До)'))
#     before_obv = models.FloatField(default=0, verbose_name=_('Обводненность (До)'))
#     before_oil = models.FloatField(default=0, verbose_name=_('Нефть (До)'))
#     start_date = models.DateField(blank=False, verbose_name=_('Дата начало'))
#     end_date = models.DateField(blank=False, verbose_name=_('Дата конец'))
#     work = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Работа'))
#     after_fluid = models.FloatField(default=0, verbose_name=_('Жидкость (После)'))
#     after_obv = models.FloatField(default=0, verbose_name=_('Обводненность (После)'))
#     after_oil = models.FloatField(default=0, verbose_name=_('Нефть (После)'))
#
#     class Meta:
#         verbose_name = _("Последние десять")
#         verbose_name_plural = _("Последние десять")
#
#     def __str__(self):
#         return self.name
#
#
# class N_lenta(models.Model):
#     criticality = models.CharField(max_length=5, blank=True, default="", verbose_name=_('Критичность'))
#     # enum -- #######################################################################################
#     extraction = models.CharField(max_length=50, blank=True, default="", verbose_name=_('Экстракция'))
#     event = models.CharField(max_length=45, blank=True, default="", verbose_name=_('Мероприятие'))
#     # enum -- #######################################################################################
#     status = models.CharField(max_length=50, blank=True, default="", verbose_name=_('Статус'))
#     oil_field = models.CharField(max_length=45, blank=True, default="", verbose_name=_('Нефть'))
#     agzu = models.CharField(max_length=45, blank=True, default="", verbose_name=_('АГЗУ'))
#     well = models.CharField(max_length=45, blank=True, default="", verbose_name=_('Скважина'))
#     otvod = models.CharField(max_length=45, blank=True, default="", verbose_name=_('Отвод'))
#     opened = models.TimeField(blank=False, verbose_name=_('Открыто'))
#     closed = models.TimeField(blank=False, verbose_name=_('Закрыто'))
#     user_name = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Имя пользователя'))
#     user_email = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Почта пользователя'))
#     delta = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Дельта'))
#     comment = models.CharField(max_length=400, blank=True, default="", verbose_name=_('Комментарий'))
#
#     class Meta:
#         verbose_name = _("Лента")
#         verbose_name_plural = _("Ленты")
#
#     def __str__(self):
#         return self.name
#
#
# class N_lenta_arch(models.Model):
#     criticality = models.CharField(max_length=5, blank=True, default="", verbose_name=_('Критичность'))
#     # enum -- #######################################################################################
#     extraction = models.CharField(max_length=50, blank=True, default="", verbose_name=_('Экстракция'))
#     event = models.CharField(max_length=45, blank=True, default="", verbose_name=_('Мероприятие'))
#     # enum -- #######################################################################################
#     status = models.CharField(max_length=50, blank=True, default="", verbose_name=_('Статус'))
#     oil_field = models.CharField(max_length=45, blank=True, default="", verbose_name=_('Нефть'))
#     agzu = models.CharField(max_length=45, blank=True, default="", verbose_name=_('АГЗУ'))
#     well = models.CharField(max_length=45, blank=True, default="", verbose_name=_('Скважина'))
#     otvod = models.CharField(max_length=45, blank=True, default="", verbose_name=_('Отвод'))
#     opened = models.TimeField(blank=False, verbose_name=_('Открыто'))
#     closed = models.TimeField(blank=False, verbose_name=_('Закрыто'))
#     user_name = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Имя пользователя'))
#     user_email = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Почта пользователя'))
#     delta = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Дельта'))
#     comment = models.CharField(max_length=400, blank=True, default="", verbose_name=_('Комментарий'))
#
#     class Meta:
#         verbose_name = _("Лента (архив)")
#         verbose_name_plural = _("Ленты (архив)")
#
#     def __str__(self):
#         return self.name
#
#
# class N_ngdu(models.Model):
#     name = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Название'))
#     code = models.CharField(max_length=20, blank=True, default="", verbose_name=_('Код'))
#
#     class Meta:
#         verbose_name = _("НГДУ")
#         verbose_name_plural = _("НГДУ")
#
#     def __str__(self):
#         return self.name
#
#
# class N_oil_fields(models.Model):
#     oil_filed = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Нефть'))
#     name = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Название'))
#     ngdu = models.CharField(max_length=255, blank=True, default="", verbose_name=_('НГДУ'))
#     annual_plan = models.IntegerField(default=0, verbose_name=_('Годовой план'))
#
#     2
#     hour_name = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Название 2-х часовки'))
#     start_time = models.CharField(max_length=45, blank=True, default="", verbose_name=_('Время начало'))
#     end_time = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Время конец'))
#     name_for_isu = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Название для ИСУ'))
#
#     class Meta:
#         verbose_name = _("Поле нефть")
#         verbose_name_plural = _("Поле нефти")
#
#     def __str__(self):
#         return self.name
#
#
# class N_pressure_plst(models.Model):
#     oil_filed = models.CharField(max_length=45, blank=True, default="", verbose_name=_('Нефть'))
#     well = models.CharField(max_length=45, blank=True, default="", verbose_name=_('Скважина'))
#     date = models.DateField(blank=False, verbose_name=_('Дата'))
#     pressure = models.FloatField(default=0, verbose_name=_('Давление'))
#     well_id = models.IntegerField(default=0, verbose_name=_('ID скважины'))
#
#     class Meta:
#         verbose_name = _("Давление (плст)")
#         verbose_name_plural = _("Давление (плст)")
#
#     def __str__(self):
#         return self.name
#
#
# class N_pressure_zab(models.Model):
#     oil_filed = models.CharField(max_length=45, blank=True, default="", verbose_name=_('Нефть'))
#     well = models.CharField(max_length=45, blank=True, default="", verbose_name=_('Скважина'))
#     date = models.DateField(blank=False, verbose_name=_('Дата'))
#     pressure = models.FloatField(default=0, verbose_name=_('Давление'))
#     well_id = models.IntegerField(default=0, verbose_name=_('ID скважины'))
#
#     class Meta:
#         verbose_name = _("Давление (заб)")
#         verbose_name_plural = _("Давление (заб)")
#
#     def __str__(self):
#         return self.name
#
#
# class N_profitability_wells(models.Model):
#     well_code = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Код скважины'))
#     income = models.IntegerField(default=0, verbose_name=_('Доход'))
#     expense = models.IntegerField(default=0, verbose_name=_('Расход'))
#     # double field -- ##############################################################
#     profitability = models.FloatField(default=0, verbose_name=_('Рентабельность'))
#     neft = models.IntegerField(default=0, verbose_name=_('Нефть'))
#     fon = models.IntegerField(default=0, verbose_name=_('Фон'))
#
#     class Meta:
#         verbose_name = _("Рентабельность скважины")
#         verbose_name_plural = _("Рентабельность скважин")
#
#     def __str__(self):
#         return self.name
#
#
# class N_prorva_levels(models.Model):
#     level = models.IntegerField(default=0, verbose_name=_('Уровень'))
#
#     class Meta:
#         verbose_name = _("Прорва уровень")
#         verbose_name_plural = _("Прорва уровни")
#
#     def __str__(self):
#         return self.name
#
#
# class N_prorva_park(models.Model):
#     time = models.CharField(max_length=45, blank=True, default="", verbose_name=_('Время'))
#     rvs1 = models.FloatField(default=0, verbose_name=_('РВС - 1'))
#     rvs4 = models.FloatField(default=0, verbose_name=_('РВС - 4'))
#     rvs5 = models.FloatField(default=0, verbose_name=_('РВС - 5'))
#     rvs6 = models.FloatField(default=0, verbose_name=_('РВС - 6'))
#     rvs7 = models.FloatField(default=0, verbose_name=_('РВС - 7'))
#     rvs8G = models.FloatField(default=0, verbose_name=_('РВС - 8G'))
#     rvs9 = models.FloatField(default=0, verbose_name=_('РВС - 9'))
#     rvs10 = models.FloatField(default=0, verbose_name=_('РВС - 10'))
#     oil_all = models.FloatField(default=0, verbose_name=_('Общая нефть'))
#     oil_all_stock_tank = models.FloatField(default=0, verbose_name=_('Общая нефть сточного РВС'))
#     oil_out = models.FloatField(default=0, verbose_name=_('Нефть (из)'))
#     oil_in = models.FloatField(default=0, verbose_name=_('Нефть (в)'))
#     fluid_in = models.FloatField(default=0, verbose_name=_('Жидкость (в)'))
#     wat_in = models.FloatField(default=0, verbose_name=_('Вода (в)'))
#
#     class Meta:
#         verbose_name = _("Прорва (парк)")
#         verbose_name_plural = _("Прорва (парк)")
#
#     def __str__(self):
#         return self.name
#
#
# class N_prs_devices(models.Model):
#     devices = models.IntegerField(default=0, verbose_name=_('Прибор'))
#     ownerid = models.IntegerField(default=0, verbose_name=_('ID владельца'))
#
#     class Meta:
#         verbose_name = _("ПРС прибор")
#         verbose_name_plural = _("ПРС приборы")
#
#     def __str__(self):
#         return self.name
#
#
# class N_prs_norm(models.Model):
#     work_code = models.IntegerField(default=0, verbose_name=_('Код работы'))
#     code_type = models.IntegerField(default=0, verbose_name=_('Тип кода'))
#     work_norm = models.FloatField(default=0, verbose_name=_('Норма работы'))
#     work_desc = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Наименование работы'))
#
#     class Meta:
#         verbose_name = _("ПРС (норма)")
#         verbose_name_plural = _("ПРС (нормы)")
#
#     def __str__(self):
#         return self.name
#
#
# class N_prs_work_time(models.Model):
#     device_id = models.IntegerField(default=0, verbose_name=_('ID прибора'))
#     crew_id = models.IntegerField(default=0, verbose_name=_('ID экипажа'))
#     oil_field = models.CharField(max_length=45, blank=True, default="", verbose_name=_('Нефть'))
#     well_id = models.CharField(max_length=45, blank=True, default="", verbose_name=_('ID скважины'))
#     date = models.DateField(blank=False, verbose_name=_('Дата'))
#     work_code = models.IntegerField(default=0, verbose_name=_('Код работы'))
#     work_time = models.FloatField(default=0, verbose_name=_('Время работы)'))
#     norm_time = models.FloatField(default=0, verbose_name=_('Время нормы)'))
#     diff = models.FloatField(default=0, verbose_name=_('Разница'))
#
#     class Meta:
#         verbose_name = _("ПРС (Время работы)")
#         verbose_name_plural = _("ПРС (Время работ)")
#
#     def __str__(self):
#         return self.name
#
#
# class N_report_balance(models.Model):
#     oil_field = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Нефть'))
#     date = models.DateField(blank=False, verbose_name=_('Дата'))
#     zamer_fluid = models.FloatField(default=0, verbose_name=_('Замер (жидкость))'))
#     park_fluid = models.FloatField(default=0, verbose_name=_('Парк (жидкость))'))
#     zamer_oil = models.FloatField(default=0, verbose_name=_('Замер (нефть)'))
#     park_oil = models.FloatField(default=0, verbose_name=_('Парк (нефть)'))
#
#     class Meta:
#         verbose_name = _("Отчет по балансу")
#         verbose_name_plural = _("Отчеты по балансам")
#
#     def __str__(self):
#         return self.name
#
#
# class N_reverse_calculations(models.Model):
#     oil_field = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Нефть'))
#     extraction = models.CharField(max_length=5, blank=True, default="", verbose_name=_('Экстракция'))
#     date = models.DateField(blank=False, verbose_name=_('Дата'))
#     zamer = models.FloatField(default=0, verbose_name=_('Замер'))
#     park = models.FloatField(default=0, verbose_name=_('Парк)'))
#     diff = models.FloatField(default=0, verbose_name=_('Разница)'))
#
#     class Meta:
#         verbose_name = _("Обратный расчет")
#         verbose_name_plural = _("Обратные расчеты")
#
#     def __str__(self):
#         return self.name
#
#
# class N_uaz_levels(models.Model):
#     level = models.IntegerField(default=0, verbose_name=_('Уровень'))
#     rgs1_vol = models.FloatField(default=0, verbose_name=_('РГС - 1'))
#     rgs2_vol = models.FloatField(default=0, verbose_name=_('РГС - 2)'))
#     rgs3_vol = models.FloatField(default=0, verbose_name=_('РГС - 3)'))
#     rgs4_vol = models.FloatField(default=0, verbose_name=_('РГС - 4)'))
#     rvs_vol = models.FloatField(default=0, verbose_name=_('РВС)'))
#
#     class Meta:
#         verbose_name = _("УАЗ (Уровень)")
#         verbose_name_plural = _("УАЗ (Уровни)")
#
#     def __str__(self):
#         return self.name
#
#
# class N_uaz_park(models.Model):
#     time = models.CharField(max_length=20, blank=True, default="", verbose_name=_('Время'))
#     rgs1_wat = models.FloatField(default=0, verbose_name=_('РГС - 1 (Вода)'))
#     rgs2_wat = models.FloatField(default=0, verbose_name=_('РГС - 2 (Вода)'))
#     rgs3_wat = models.FloatField(default=0, verbose_name=_('РГС - 3 (Вода)'))
#     rgs4_wat = models.FloatField(default=0, verbose_name=_('РГС - 4 (Вода)'))
#     rgs3_oil = models.FloatField(default=0, verbose_name=_('РГС - 3 (Нефть)'))
#     rgs4_oil = models.FloatField(default=0, verbose_name=_('РГС - 4 (Нефть)'))
#     rvs_oil = models.FloatField(default=0, verbose_name=_('РВС (Нефть)'))
#     oil_all = models.FloatField(default=0, verbose_name=_('Нефть (Общее)'))
#     wat_all = models.FloatField(default=0, verbose_name=_('Вода (Общее)'))
#     oil1_out = models.FloatField(default=0, verbose_name=_('Нефть - 1 (Из)'))
#     oil2_out = models.FloatField(default=0, verbose_name=_('Нефть - 2 (Из)'))
#     wat_out = models.FloatField(default=0, verbose_name=_('Вода (Из)'))
#     oil_in = models.FloatField(default=0, verbose_name=_('Нефть (в)'))
#     wat_in = models.FloatField(default=0, verbose_name=_('Вода (в)'))
#     fld_in = models.FloatField(default=0, verbose_name=_('Жидкость (в)'))
#
#     class Meta:
#         verbose_name = _("УАЗ (парк)")
#         verbose_name_plural = _("УАЗ (парк)")
#
#     def __str__(self):
#         return self.name
#
#
# class N_users(models.Model):
#     login = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Логин'))
#     name = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Имя'))
#     password = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Пароль'))
#     is_admin = models.IntegerField(default=0, verbose_name=_('Администратор'))
#     available_ngdu_id = models.CharField(max_length=255, blank=True, default="", verbose_name=_('ID доступа НГДУ'))
#
#     class Meta:
#         verbose_name = _("Пользователь")
#         verbose_name_plural = _("Пользователи")
#
#     def __str__(self):
#         return self.name
#
#
# class N_vmb_park(models.Model):
#     time = models.CharField(max_length=20, blank=True, default="", verbose_name=_('Время'))
#     rgs1_wat = models.FloatField(default=0, verbose_name=_('РГС - 1 (Вода)'))
#     rgs2_wat = models.FloatField(default=0, verbose_name=_('РГС - 2 (Вода)'))
#     rgs3_wat = models.FloatField(default=0, verbose_name=_('РГС - 3 (Вода)'))
#     rgs4_wat = models.FloatField(default=0, verbose_name=_('РГС - 4 (Вода)'))
#     rgs3_oil = models.FloatField(default=0, verbose_name=_('РГС - 3 (Нефть)'))
#     rgs4_oil = models.FloatField(default=0, verbose_name=_('РГС - 4 (Нефть)'))
#     rvs_oil = models.FloatField(default=0, verbose_name=_('РВС (Нефть)'))
#     oil_all = models.FloatField(default=0, verbose_name=_('Нефть (Общее)'))
#     wat_all = models.FloatField(default=0, verbose_name=_('Вода (Общее)'))
#     oil1_out = models.FloatField(default=0, verbose_name=_('Нефть - 1 (Из)'))
#     oil2_out = models.FloatField(default=0, verbose_name=_('Нефть - 2 (Из)'))
#     wat_out = models.FloatField(default=0, verbose_name=_('Вода (Из)'))
#     oil_in = models.FloatField(default=0, verbose_name=_('Нефть (в)'))
#     wat_in = models.FloatField(default=0, verbose_name=_('Вода (в)'))
#     fld_in = models.FloatField(default=0, verbose_name=_('Жидкость (в)'))
#
#     class Meta:
#         verbose_name = _("ВМБ (парк)")
#         verbose_name_plural = _("ВМБ (парк)")
#
#     def __str__(self):
#         return self.name
#
#
# class N_vmt_park(models.Model):
#     time = models.CharField(max_length=20, blank=True, default="", verbose_name=_('Время'))
#     rvs1 = models.FloatField(default=0, verbose_name=_('РВС - 1'))
#     rvs5 = models.FloatField(default=0, verbose_name=_('РВС - 5'))
#     rvs6 = models.FloatField(default=0, verbose_name=_('РВС - 6'))
#     rvs7 = models.FloatField(default=0, verbose_name=_('РВС - 7'))
#     rvs9 = models.FloatField(default=0, verbose_name=_('РВС - 9'))
#     rvs8_wat = models.FloatField(default=0, verbose_name=_('РВС - 8 (Вода)'))
#     oil_all = models.FloatField(default=0, verbose_name=_('Нефть (Общее)'))
#     wat_all = models.FloatField(default=0, verbose_name=_('Вода (Общее)'))
#     oil_out = models.FloatField(default=0, verbose_name=_('Нефть (Из)'))
#     wat_out = models.FloatField(default=0, verbose_name=_('Вода (Из)'))
#     oil_in_zholdybai = models.FloatField(default=0, verbose_name=_('Нефть (в Жолдыбай)'))
#     oil_in = models.FloatField(default=0, verbose_name=_('Нефть (в)'))
#     wat_in = models.FloatField(default=0, verbose_name=_('Вода (в)'))
#     fld_in = models.FloatField(default=0, verbose_name=_('Жидкость (в)'))
#     oil_to_cppn = models.FloatField(default=0, verbose_name=_('Нефть ЦППН'))
#     oil_to_cppn_nak = models.FloatField(default=0, verbose_name=_('Нефть ЦППН (с накоплением)'))
#     wat_to_ppd = models.FloatField(default=0, verbose_name=_('Вода ППД'))
#     wat_to_ppd_nak = models.FloatField(default=0, verbose_name=_('Вода ППД (с накоплением)'))
#     wat_to_sin = models.FloatField(default=0, verbose_name=_('Вода СИН'))
#     wat_to_sin_nak = models.FloatField(default=0, verbose_name=_('Вода СИН (с накоплением)'))
#     oil_from_zholdybai = models.FloatField(default=0, verbose_name=_('Нефть Жолдыбай'))
#     oil_from_zholdybai_nak = models.FloatField(default=0, verbose_name=_('Нефть Жолдыбай (с накоплением)'))
#     ppd = models.FloatField(default=0, verbose_name=_('ППД'))
#     sin = models.FloatField(default=0, verbose_name=_('СИН'))
#     oil_out_vmt = models.FloatField(default=0, verbose_name=_('Нефть ВМТ'))
#     oil_out_vmt_nak = models.FloatField(default=0, verbose_name=_('Нефть ВМТ (с накоплением)'))
#
#     class Meta:
#         verbose_name = _("ВМТ (парк)")
#         verbose_name_plural = _("ВМТ (парк)")
#
#     def __str__(self):
#         return self.name
#
#
# class N_well_ids(models.Model):
#     well = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Скважина'))
#     well_id = models.CharField(max_length=255, blank=True, default="", verbose_name=_('ID скважины'))
#     oil_filed = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Нефть'))
#
#     class Meta:
#         verbose_name = _("ID скважины")
#         verbose_name_plural = _("ID скважин")
#
#     def __str__(self):
#         return self.name
#
#
# class N_well_matrix(models.Model):
#     oil_field = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Нефть'))
#     well = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Скважина'))
#     zamer = models.FloatField(default=0, verbose_name=_('Замер'))
#     agzu = models.CharField(max_length=45, blank=True, default="", verbose_name=_('АГЗУ'))
#     otvod = models.IntegerField(default=0, verbose_name=_('Отвод'))
#     tr_fluid = models.FloatField(default=0, verbose_name=_('Тех/режим (Жидкость)'))
#     tr_oil = models.FloatField(default=0, verbose_name=_('Тех/режим (Нефть)'))
#     tr_water = models.FloatField(default=0, verbose_name=_('Тех/режим (Обводненность)'))
#     zamer_oil = models.FloatField(default=0, verbose_name=_('Замер (Нефть)'))
#     delta_oil = models.FloatField(default=0, verbose_name=_('Дельта (Нефть)'))
#     fon_oil = models.IntegerField(default=0, verbose_name=_('Фон (Нефть)'))
#     delta_fluid = models.FloatField(default=0, verbose_name=_('Дельта (Жидкость)'))
#     fon_fluid = models.IntegerField(default=0, verbose_name=_('Фон (Жидкость)'))
#     well_id = models.CharField(max_length=45, blank=True, default="", verbose_name=_('ID Скважины'))
#     status = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Статус'))
#     last_actual_update = models.DateTimeField(blank=False, verbose_name=_('Последнее актульное обновление'))
#
#     class Meta:
#         verbose_name = _("Матрица скважины")
#         verbose_name_plural = _("Матрица скважин")
#
#     def __str__(self):
#         return self.name
#
#
# class N_well_matrix_arch(models.Model):
#     date = models.DateField(blank=False, verbose_name=_('Дата'))
#     oil_field = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Нефть'))
#     well = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Скважина'))
#     zamer = models.FloatField(default=0, verbose_name=_('Замер'))
#     agzu = models.CharField(max_length=45, blank=True, default="", verbose_name=_('АГЗУ'))
#     otvod = models.IntegerField(default=0, verbose_name=_('Отвод'))
#     tr_fluid = models.FloatField(default=0, verbose_name=_('Тех/режим (Жидкость)'))
#     tr_oil = models.FloatField(default=0, verbose_name=_('Тех/режим (Нефть)'))
#     tr_water = models.FloatField(default=0, verbose_name=_('Тех/режим (Обводненность)'))
#     zamer_oil = models.FloatField(default=0, verbose_name=_('Замер (Нефть)'))
#     delta_oil = models.FloatField(default=0, verbose_name=_('Дельта (Нефть)'))
#     fon_oil = models.IntegerField(default=0, verbose_name=_('Фон (Нефть)'))
#     delta_fluid = models.FloatField(default=0, verbose_name=_('Дельта (Жидкость)'))
#     fon_fluid = models.IntegerField(default=0, verbose_name=_('Фон (Жидкость)'))
#     well_id = models.CharField(max_length=45, blank=True, default="", verbose_name=_('ID Скважины'))
#     status = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Статус'))
#     last_actual_update = models.DateTimeField(blank=False, verbose_name=_('Последнее актульное обновление'))
#
#     class Meta:
#         verbose_name = _("Матрица скважины (архив)")
#         verbose_name_plural = _("Матрица скважин (архив)")
#
#     def __str__(self):
#         return self.name
#
#
# class N_well_matrix_t(models.Model):
#     oil_field = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Нефть'))
#     well = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Скважина'))
#     zamer = models.FloatField(default=0, verbose_name=_('Замер'))
#     agzu = models.CharField(max_length=255, blank=True, default="", verbose_name=_('АГЗУ'))
#     otvod = models.IntegerField(default=0, verbose_name=_('Отвод'))
#     tr_fluid = models.FloatField(default=0, verbose_name=_('Тех/режим (Жидкость)'))
#     tr_oil = models.FloatField(default=0, verbose_name=_('Тех/режим (Нефть)'))
#     tr_water = models.FloatField(default=0, verbose_name=_('Тех/режим (Обводненность)'))
#     fon = models.IntegerField(default=0, verbose_name=_('Фон'))
#     delta = models.FloatField(default=0, verbose_name=_('Дельта'))
#     zamer_oil = models.FloatField(default=0, verbose_name=_('Замер (Нефть)'))
#     delta_oil = models.FloatField(default=0, verbose_name=_('Дельта (Нефть)'))
#     fon_oil = models.IntegerField(default=0, verbose_name=_('Фон (Нефть)'))
#     delta_fluid = models.FloatField(default=0, verbose_name=_('Дельта (Жидкость)'))
#     fon_fluid = models.IntegerField(default=0, verbose_name=_('Фон (Жидкость)'))
#     delta_percent_fluid = models.IntegerField(default=0, verbose_name=_('Дельта (% Жидкость)'))
#     delta_percent_oil = models.IntegerField(default=0, verbose_name=_('Дельта (% Нефть)'))
#
#     class Meta:
#         verbose_name = _("Матрица скважины")
#         verbose_name_plural = _("Матрица скважин")
#
#     def __str__(self):
#         return self.name
#
#
# class N_well_stock(models.Model):
#     oil_field = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Нефть'))
#     key = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Ключ'))
#     value = models.IntegerField(default=0, verbose_name=_('Значение'))
#
#     class Meta:
#         verbose_name = _("Сток скважины")
#         verbose_name_plural = _("Сток скважин")
#
#     def __str__(self):
#         return self.name
#
#
# class N_wincctags(models.Model):
#     oil_field = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Нефть'))
#     tag_key = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Ключ тэга'))
#     tag_value = models.CharField(max_length=255, blank=True, default="", verbose_name=_('Значение тэга'))
#     last_update = models.DateTimeField(blank=False, verbose_name=_('Последнее обновление'))
#     last_actual_update = models.DateTimeField(blank=False, verbose_name=_('Последнее актульное обновление'))
#
#     class Meta:
#         verbose_name = _("ВИНСС тэг")
#         verbose_name_plural = _("ВИНСС тэги")
#
#     def __str__(self):
#         return self.name
#
#
# class z_wincctags(models.Model):
#     tag = models.CharField(max_length=50, blank=True, default="", verbose_name=_('Тэг'))
#     value = models.CharField(max_length=50, blank=True, default="", verbose_name=_('Значение'))
#
#     class Meta:
#         verbose_name = _("(Z) ВИНСС тэг")
#         verbose_name_plural = _("(Z) ВИНСС тэги")
#
#     def __str__(self):
#         return self.name
#
#
# from django.db import models
#
# # Create your models here.
