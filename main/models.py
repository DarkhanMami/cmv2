import uuid

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

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
    teh_rej_fluid = models.FloatField(default=0, verbose_name=_('Техрежим жидкости'))
    teh_rej_oil = models.FloatField(default=0, verbose_name=_('Техрежим нефти'))
    teh_rej_water = models.FloatField(default=0, verbose_name=_('Обводненность'))

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


class WellMatrix(models.Model):
    well = models.ForeignKey(Well, blank=False, null=False, on_delete=models.CASCADE, related_name='wells')

    filling = models.FloatField(default=0, verbose_name=_('Заполнение насоса'))
    fluid_agzu = models.FloatField(default=0, verbose_name=_('Жидкость (АГЗУ)'))
    fluid_isu = models.FloatField(default=0, verbose_name=_('Жидкость (ИСУ)'))

    shortage_isu = models.FloatField(default=0, verbose_name=_('Недобор (ИСУ)'))
    shortage_prs = models.FloatField(default=0, verbose_name=_('Недобор (ПРС)'))
    shortage_wait = models.FloatField(default=0, verbose_name=_('Недобор (Ожид.тех)'))

    brigade_num = models.IntegerField(default=0, verbose_name=_('Номер бригады'))
    ts_num = models.CharField(max_length=20, blank=True, default="", verbose_name=_('Номер ТС'))

    well_stop = models.FloatField(default=0, verbose_name=_('Остановы'))
    oil_loss = models.FloatField(default=0, verbose_name=_('Потери'))

    active = models.BooleanField(default=False, verbose_name=_('Активный'))
    performance = models.FloatField(default=100, verbose_name=_('Производительность'))
    has_isu = models.BooleanField(default=False, verbose_name=_('Оснащен ИСУ'))

    class Meta:
        verbose_name = _("Матрица")
        verbose_name_plural = _("Матрица")


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
    gos_num = models.CharField(max_length=20, blank=False, null=False, unique=True, db_index=True, verbose_name=_('Гос номер'))
    marka = models.CharField(max_length=50, verbose_name=_('Марка'))
    type = models.CharField(max_length=50, verbose_name=_('Тип'))
    total_days = models.IntegerField(default=30, verbose_name=_('Всего дней'))
    in_work = models.IntegerField(default=30, verbose_name=_('В работу'))
    in_rem = models.IntegerField(default=30, verbose_name=_('В ремонте'))
    day_off = models.IntegerField(default=30, verbose_name=_('Выходной'))
    month = models.IntegerField(default=30, verbose_name=_('Месяц'))
    year = models.IntegerField(default=30, verbose_name=_('Год'))
    field = models.CharField(max_length=50, verbose_name=_('ПСП'))
    kip = models.FloatField(default=100, verbose_name=_('КИП'))
    ktg = models.FloatField(default=100, verbose_name=_('КТГ'))

    class Meta:
        verbose_name = _("Транспортное средство")
        verbose_name_plural = _("Транспортные средства")

    def __str__(self):
        return self.gos_num

