from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group
import smtplib

from main import models
from main.models import Field, Well, WellMatrix, TS, Depression, ProdProfile, GSM, Dynamogram, Imbalance, \
    ImbalanceHistory, ImbalanceHistoryAll, SumWellInField, WellEvents, FieldMatrix, PrsDevice, Constant, \
    Recommendation, Events, MailUser, MailSettings, MailHistory, Wattmetrogram


class CustomUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

    class Meta(UserCreationForm.Meta):
        model = models.User
        fields = '__all__'


class CustomUserChangeForm(UserChangeForm):

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)

    class Meta(UserChangeForm.Meta):
        model = models.User
        fields = '__all__'


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('email', 'is_admin')
    list_filter = ('is_admin', 'type')
    fieldsets = (
        (None, {'fields': ('email', 'name', 'password', 'type')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'type', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

    def has_module_permission(self, request):
        if request.user.is_authenticated and (request.user.type == "Администратор"):
            return True
        else:
            return False


admin.site.unregister(Group)


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(PrsDevice)
class PrsDeviceAdmin(admin.ModelAdmin):
    list_display = ('num',)


@admin.register(Well)
class WellAdmin(admin.ModelAdmin):
    list_display = ('name', 'well_id', 'tbd_id', 'gzu', 'horizon', 'production_type', 'server', 'has_isu', 'tpn',
                    'pump_depth')
    search_fields = ('name',)
    list_filter = ('field',)


@admin.register(WellMatrix)
class WellMatrixAdmin(admin.ModelAdmin):
    list_display = ('well', 'filling', 'fluid_agzu', 'fluid_isu', 'tbd_fluid', 'teh_rej_fluid', 'teh_rej_oil',
                    'teh_rej_water', 'park_fluid', 'park_oil', 'kpn', 'dyn_level', 'p_zab', 'p_plast', 'status',
                    'sdmo_status', 'pump_speed', 'electric_cons', 'timestamp')
    search_fields = ('well__name',)
    list_filter = ('well__field',)


@admin.register(WellEvents)
class WellEventsAdmin(admin.ModelAdmin):
    list_display = ('well', 'event_type', 'event', 'beg', 'end')
    search_fields = ('well__name',)
    list_filter = ('well__field',)


@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    list_display = ('field', 'event', 'event_type', 'fact', 'plan', 'coef', 'price', 'effect')
    list_filter = ('event_type', 'field')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('well', 'kpn', 'event', 'timestamp')
    search_fields = ('well__name',)
    list_filter = ('well__field',)


@admin.register(Depression)
class DepressionAdmin(admin.ModelAdmin):
    list_display = ('well', 'densityPL', 'densityZB', 'densityDiff', 'fluid_av', 'timestamp')
    search_fields = ('well',)


@admin.register(TS)
class TSAdmin(admin.ModelAdmin):
    list_display = ('gos_num', 'marka', 'type', 'total_days', 'in_work', 'in_rem', 'day_off',
                    'month', 'year', 'field', 'kip', 'ktg')
    search_fields = ('gos_num',)
    list_filter = ('field',)


@admin.register(GSM)
class GSMAdmin(admin.ModelAdmin):
    list_display = ('gos_num', 'type', 'year', 'month', 'field', 'gsm_type', 'sum', 'quantity')
    search_fields = ('gos_num',)
    list_filter = ('field',)


@admin.register(ProdProfile)
class ProdProfileAdmin(admin.ModelAdmin):
    list_display = ('well', 'well_pair', 'pre_fluid', 'post_fluid', 'pre_oil', 'post_oil', 'pre_obv', 'post_obv', 'effect')
    search_fields = ('well',)


@admin.register(Dynamogram)
class DynamogramAdmin(admin.ModelAdmin):
    list_display = ('well', 'timestamp')
    search_fields = ('well',)


@admin.register(Wattmetrogram)
class WattmetrogramAdmin(admin.ModelAdmin):
    list_display = ('well', 'timestamp')
    search_fields = ('well',)


class ImbalanceHistoryAdmin(admin.StackedInline):
    model = ImbalanceHistory
    extra = 0
    # readonly_fields = []

    # This will help you to disable delete functionaliyt
    # def has_delete_permission(self, request, obj=None):
    #     return False


@admin.register(Imbalance)
class ImbalanceAdmin(admin.ModelAdmin):
    list_display = ('well', 'imbalance', 'avg_1997', 'timestamp')
    search_fields = ('well',)
    list_filter = ('well__field',)
    # inlines = [ImbalanceHistoryAdmin, ]


@admin.register(ImbalanceHistoryAll)
class ImbalanceHistoryAllAdmin(admin.ModelAdmin):
    list_display = ('count', 'percent', 'timestamp')


@admin.register(SumWellInField)
class SumWellInFieldAdmin(admin.ModelAdmin):
    list_display = ('field', 'timestamp')


@admin.register(FieldMatrix)
class FieldMatrixAdmin(admin.ModelAdmin):
    list_display = ('field', 'timestamp')


@admin.register(Constant)
class ConstantAdmin(admin.ModelAdmin):
    list_display = ('name', 'min', 'max')


class MailUserAdmin(admin.StackedInline):
    model = MailUser
    extra = 3


@admin.register(MailSettings)
class MailSettingsAdmin(admin.ModelAdmin):
    list_display = ('field', 'type', 'body', 'freq')
    list_filter = ('field', 'type')
    inlines = [MailUserAdmin, ]
    actions = ['send_manually']

    def send_manually(self, request, queryset):
        mail_sender = smtplib.SMTP('smtp.gmail.com', 587)
        mail_sender.ehlo()
        mail_sender.starttls()
        mail_sender.ehlo()
        mail_sender.login("noreply@dlc.kz", "Xm*6%R7u")
        for mail_object in queryset:
            mail_users = MailUser.objects.filter(mail=mail_object)
            for mail_user in mail_users:
                send_to = mail_user.email
                text = 'Уважаемый(ая) ' + mail_user.name + ', ' + '\n' \
                       + 'Ручная отправка соообщения.' + '\n' + '\n' + '\n' \
                       + 'С уважением, noreply@dlc.kz!'
                body = "\r\n".join((
                    "From: %s" % 'noreply@dlc.kz',
                    "To: %s" % send_to,
                    "Subject: %s" % mail_object.body + ': ' + mail_object.type,
                    "",
                    text
                ))
                mail_sender.sendmail('noreply@dlc.kz', [send_to], body.encode('utf-8'))
            MailHistory.objects.create(mail=mail_object)

    send_manually.short_description = "Отправить вручную"


@admin.register(MailHistory)
class MailHistoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'mail', 'timestamp')
    list_filter = ('mail__field', 'mail__type')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False



