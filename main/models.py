import uuid

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext as _
from tinymce.models import HTMLField


def uploaded_filename(instance, filename):
    """
    Scramble / uglify the filename of the uploaded file, but keep the files extension (e.g., .jpg or .png)
    :param instance:
    :param filename:
    :return:
    """
    extension = filename.split(".")[-1]
    return "{}/{}.{}".format(instance.pk, uuid.uuid4(), extension)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError(_('Users must have an email address'))

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name=_('Email'),
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=1024, blank=True, default="")
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    ADMINISTRATOR = "Администратор"
    MANAGER = "Менеджер"


    TYPE_CHOICES = (
        (ADMINISTRATOR, _('Администратор')),
        (MANAGER, _('Менеджер')),

    )

    type = models.CharField(choices=TYPE_CHOICES, default=MANAGER, max_length=100, db_index=True, verbose_name=_("Тип"))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class Field(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True, db_index=True, verbose_name=_('Название'))

    class Meta:
        verbose_name = _("Месторождение")
        verbose_name_plural = _("Месторождения")

    def __str__(self):
        return self.name


class Well(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, unique=True, db_index=True, verbose_name=_('Название'))
    field = models.ForeignKey(Field, blank=False, null=False, on_delete=models.CASCADE, related_name='fields')
    well_id = models.IntegerField(default=0, verbose_name=_('sdmo_id'))
    tbd_id = models.CharField(max_length=30, blank=True, null=True, verbose_name=_('tbd_id'))

    server1 = "192.168.241.2"
    server2 = "192.168.243.2"
    server3 = "192.168.236.2"
    server4 = "192.168.128.2" 
    SERVERS = (
        (server1, _('192.168.241.2')),
        (server2, _('192.168.243.2')),
        (server3, _('192.168.236.2')),
        (server4, _('192.168.128.2')),
    )

    server = models.CharField(choices=SERVERS,default=server1, max_length=15, verbose_name=_("Сервер"))

    has_isu = models.BooleanField(default= False, verbose_name=_("Оснащен ИСУ"))

    SGN = "ШГН"
    EVN = "ЭВН" 
    PRODUCTION_TYPES = (
        (SGN, _('ШГН')),
        (EVN, _('ЭВН')),
    )

    production_type = models.CharField(choices=PRODUCTION_TYPES, default=SGN, max_length=100, verbose_name=_("Технология добычи"))

    class Meta:
        verbose_name = _("Скважина")
        verbose_name_plural = _("Скважины")

    def __str__(self):
        return self.name


class Imbalance(models.Model):
    well = models.ForeignKey(Well, blank=False, null=False, on_delete=models.CASCADE, related_name='imb_wells')
    imbalance = models.FloatField(default=0, verbose_name=_('Неуравновешенность'))
    avg_1997 = models.FloatField(default=0, verbose_name=_('Заполнения насоса'))
    timestamp = models.DateTimeField(blank=True, null=True, verbose_name=_('Дата опроса'))

    class Meta:
        verbose_name = _("Неуравновешенность")
        verbose_name_plural = _("Неуравновешенность")


class ImbalanceHistory(models.Model):
    imb = models.ForeignKey(Imbalance, blank=False, null=False, on_delete=models.CASCADE, related_name='imb')
    well = models.ForeignKey(Well, blank=False, null=False, on_delete=models.CASCADE, related_name='imb_wells_history')
    imbalance = models.FloatField(default=0, verbose_name=_('Неуравновешенность'))
    avg_1997 = models.FloatField(default=0, verbose_name=_('Заполнения насоса'))
    timestamp = models.DateTimeField(blank=True, null=True, verbose_name=_('Дата опроса'))

    class Meta:
        verbose_name = _("Неуравновешенность история")
        verbose_name_plural = _("Неуравновешенность история")


class ImbalanceHistoryAll(models.Model):
    count = models.IntegerField(default=0, verbose_name=_('Число скважен'))
    percent = models.FloatField(default=0, verbose_name=_('Процент от кольичесво скважен'))
    timestamp = models.DateTimeField(blank=True, null=True, verbose_name=_('Дата'))

    class Meta:
        verbose_name = _("Неуравновешенность история всех скважен дня")
        verbose_name_plural = _("Неуравновешенность история всех скважен дней")


class WellMatrix(models.Model):
    well = models.ForeignKey(Well, blank=False, null=False, on_delete=models.CASCADE, related_name='wells')

    filling = models.FloatField(default=0, verbose_name=_('Заполнение насоса'))
    fluid_agzu = models.FloatField(default=0, verbose_name=_('Жидкость (АГЗУ)'))
    fluid_isu = models.FloatField(default=0, verbose_name=_('Жидкость (ИСУ)'))
    shortage_isu = models.FloatField(default=0, verbose_name=_('Недобор (ИСУ)'))
    shortage_prs = models.FloatField(default=0, verbose_name=_('Недобор (ПРС)'))
    shortage_wait = models.FloatField(default=0, verbose_name=_('Недобор (Ожид.тех)'))
    teh_rej_fluid = models.FloatField(default=0, verbose_name=_('Техрежим жидкости'))
    teh_rej_oil = models.FloatField(default=0, verbose_name=_('Техрежим нефти'))
    teh_rej_water = models.FloatField(default=0, verbose_name=_('Обводненность'))

    brigade_num = models.IntegerField(default=0, verbose_name=_('Номер бригады'))
    ts_num = models.CharField(max_length=20, blank=True, default="", verbose_name=_('Номер ТС'))

    well_stop = models.FloatField(default=0, verbose_name=_('Остановы'))

    active = models.BooleanField(default=False, verbose_name=_('Активный'))
    performance = models.FloatField(default=100, verbose_name=_('Производительность'))
    has_isu = models.BooleanField(default=False, verbose_name=_('Оснащен ИСУ'))

    timestamp = models.DateField(blank=True, null=True, verbose_name=_('Дата'))

    class Meta:
        verbose_name = _("Матрица")
        verbose_name_plural = _("Матрица")


class WellEvents(models.Model):
    well = models.ForeignKey(Well, blank=False, null=False, on_delete=models.CASCADE, related_name='event_wells')

    PRS = "ПРС"
    KRS = "КРС"
    TRS = "ТРС"
    OTHER = "Прочее"

    EVENT_CHOICES = (
        (PRS, _('ПРС')),
        (KRS, _('КРС')),
        (TRS, _('ТРС')),
        (OTHER, _('Прочее')),
    )

    event_type = models.CharField(choices=EVENT_CHOICES, default=OTHER, max_length=20, verbose_name=_('Тип события'))
    event = models.CharField(max_length=200, verbose_name=_('Событие'))
    beg = models.DateTimeField(blank=False, verbose_name=_('Начало события'))
    end = models.DateTimeField(blank=False, verbose_name=_('Конец события'))

    class Meta:
        verbose_name = _("Журнал события")
        verbose_name_plural = _("Журнал событий")


class Depression(models.Model):
    well = models.ForeignKey(Well, blank=False, null=False, on_delete=models.CASCADE, related_name='depression_wells')

    densityPL = models.FloatField(default=0, verbose_name=_('Давление (Пласт)'))
    densityZB = models.FloatField(default=0, verbose_name=_('Давление (Забой)'))
    densityDiff = models.FloatField(default=0, verbose_name=_('Разница'))
    fluid_av = models.FloatField(default=0, verbose_name=_('Жидкость (ср.)'))

    timestamp = models.DateField(blank=False, verbose_name=_('Дата'))

    class Meta:
        verbose_name = _("Подбор депрессии")
        verbose_name_plural = _("Подбор депрессий")


class FieldBalance(models.Model):
    field = models.ForeignKey(Field, blank=False, null=False, on_delete=models.CASCADE, related_name='bal_fields')
    transport_balance = models.FloatField(default=0, db_index=True, verbose_name=_('Автомобильные весы (жидкость)'))
    ansagan_balance = models.FloatField(default=0, db_index=True, verbose_name=_('Весы по Ансаган (жидкость)'))
    transport_brutto = models.FloatField(default=0, db_index=True, verbose_name=_('Автомобильные весы (брутто)'))
    ansagan_brutto = models.FloatField(default=0, db_index=True, verbose_name=_('Весы по Ансаган (брутто)'))
    transport_netto = models.FloatField(default=0, db_index=True, verbose_name=_('Автомобильные весы (нетто)'))
    ansagan_netto = models.FloatField(default=0, db_index=True, verbose_name=_('Весы по Ансаган (нетто)'))
    transport_density = models.FloatField(default=0, db_index=True, verbose_name=_('Автомобильные весы (плотность)'))
    ansagan_density = models.FloatField(default=0, db_index=True, verbose_name=_('Весы по Ансаган (плотность)'))

    agzu_fluid = models.FloatField(default=0, db_index=True, verbose_name=_('Замер жидкости по скважинам'))
    agzu_oil = models.FloatField(default=0, db_index=True, verbose_name=_('Замер нефти по скважинам'))
    teh_rej_fluid = models.FloatField(default=0, db_index=True, verbose_name=_('Замер по Тех. жидкости'))
    teh_rej_oil = models.FloatField(default=0, db_index=True, verbose_name=_('Замер по Тех. нефти'))

    timestamp = models.DateField(blank=False, verbose_name=_('Дата замера'))

    class Meta:
        verbose_name = _("Баланс по месторождению")
        verbose_name_plural = _("Баланс по месторождениям")


class TS(models.Model):
    gos_num = models.CharField(max_length=20, blank=False, null=False, verbose_name=_('Гос номер'))
    marka = models.CharField(max_length=50, verbose_name=_('Марка'))
    type = models.CharField(max_length=50, verbose_name=_('Тип'))
    total_days = models.IntegerField(default=30, verbose_name=_('Всего дней'))
    in_work = models.IntegerField(default=30, verbose_name=_('В работу'))
    in_rem = models.IntegerField(default=30, verbose_name=_('В ремонте'))
    day_off = models.IntegerField(default=30, verbose_name=_('Выходной'))
    month = models.IntegerField(default=30, verbose_name=_('Месяц'))
    year = models.IntegerField(default=2019, verbose_name=_('Год'))
    field = models.CharField(max_length=50, verbose_name=_('ПСП'))
    kip = models.FloatField(default=100, verbose_name=_('КИП'))
    ktg = models.FloatField(default=100, verbose_name=_('КТГ'))

    class Meta:
        verbose_name = _("Транспортное средство")
        verbose_name_plural = _("Транспортные средства")

    def __str__(self):
        return self.gos_num


class GSM(models.Model):
    gos_num = models.CharField(max_length=50, blank=False, null=False, verbose_name=_('Гос номер'))
    type = models.CharField(max_length=100, verbose_name=_('Тип'))
    year = models.IntegerField(default=2019, verbose_name=_('Год'))
    month = models.IntegerField(default=-1, verbose_name=_('Месяц'))
    field = models.CharField(max_length=30, verbose_name=_('ПСП'))
    gsm_type = models.CharField(max_length=50, verbose_name=_('Тип ГСМ'))
    sum = models.FloatField(default=0, verbose_name=_('Сумма во ВВ'))
    quantity = models.FloatField(default=0, verbose_name=_('Количество'))

    class Meta:
        verbose_name = _("ГСМ")
        verbose_name_plural = _("ГСМ")

    def __str__(self):
        return self.gos_num


class ProdProfile(models.Model):
    well = models.ForeignKey(Well, blank=False, null=False, on_delete=models.CASCADE, related_name='prof_wells')
    well_pair = models.IntegerField(default=-1, verbose_name=_('Пара'))
    pre_fluid = models.FloatField(default=0, verbose_name=_('Жидкость (До)'))
    post_fluid = models.FloatField(default=0, verbose_name=_('Жидкость (После)'))
    pre_oil = models.FloatField(default=0, verbose_name=_('Нефть (До)'))
    post_oil = models.FloatField(default=0, verbose_name=_('Нефть (После)'))
    pre_obv = models.FloatField(default=0, verbose_name=_('Обводненность (До)'))
    post_obv = models.FloatField(default=0, verbose_name=_('Обводненность (После)'))
    effect = models.FloatField(default=0, verbose_name=_('Эффект (нефть)'))

    class Meta:
        verbose_name = _("Профиль добычи")
        verbose_name_plural = _("Профиль добычи")


class Dynamogram(models.Model):
    well = models.ForeignKey(Well, blank=False, null=False, on_delete=models.CASCADE, related_name='dyn_wells')
    x = ArrayField(models.FloatField(), blank=True)
    y = ArrayField(models.FloatField(), blank=True)
    timestamp = models.DateTimeField(blank=False, verbose_name=_('Время замера'))

    class Meta:
        verbose_name = _("Динамограмма скважины")
        verbose_name_plural = _("Динамограммы скважин")


class SumWellInField(models.Model):
    field = models.ForeignKey(Field, blank=False, null=False, on_delete=models.CASCADE, related_name='well_in_fields')

    filling = models.FloatField(default=0, verbose_name=_('Заполнение насоса'))
    fluid_agzu = models.FloatField(default=0, verbose_name=_('Жидкость (АГЗУ)'))
    fluid_isu = models.FloatField(default=0, verbose_name=_('Жидкость (ИСУ)'))

    shortage_isu = models.FloatField(default=0, verbose_name=_('Недобор (ИСУ)'))
    shortage_prs = models.FloatField(default=0, verbose_name=_('Недобор (ПРС)'))
    shortage_wait = models.FloatField(default=0, verbose_name=_('Недобор (Ожид.тех)'))

    teh_rej_fluid = models.FloatField(default=0, verbose_name=_('Техрежим жидкости'))
    teh_rej_oil = models.FloatField(default=0, verbose_name=_('Техрежим нефти'))
    teh_rej_water = models.FloatField(default=0, verbose_name=_('Обводненность'))

    well_stop = models.FloatField(default=0, verbose_name=_('Остановы'))
    performance = models.FloatField(default=100, verbose_name=_('Производительность'))
  
    timestamp = models.DateField(blank=True, null=True, verbose_name=_('Дата'))
