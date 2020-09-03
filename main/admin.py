from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group

from main import models
from main.models import Field, Well, WellMatrix, TS, Depression, ProdProfile, GSM, Dynamogram, Imbalance, \
    ImbalanceHistory, ImbalanceHistoryAll, SumWellInField, WellEvents, FieldMatrix, PrsDevice


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
    list_display = ('field', 'name', 'well_id', 'tbd_id', 'production_type', 'server', 'has_isu', 'shortage_isu',
                    'shortage_prs', 'shortage_wait', 'well_stop_prs', 'well_stop', 'rem_count', 'brigade_num', 'ts_num')
    search_fields = ('name',)
    list_filter = ('field',)


@admin.register(WellMatrix)
class WellMatrixAdmin(admin.ModelAdmin):
    list_display = ('well', 'filling', 'fluid_agzu', 'fluid_isu', 'teh_rej_fluid', 'teh_rej_oil', 'teh_rej_water',
                    'timestamp')
    search_fields = ('well',)


@admin.register(WellEvents)
class WellEventsAdmin(admin.ModelAdmin):
    list_display = ('well', 'event_type', 'event', 'beg', 'end')
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
    inlines =[ ImbalanceHistoryAdmin,]


@admin.register(ImbalanceHistoryAll)
class ImbalanceHistoryAllAdmin(admin.ModelAdmin):
    list_display = ('count', 'percent','timestamp')


@admin.register(SumWellInField)
class SumWellInFieldAdmin(admin.ModelAdmin):
    list_display = ('field', 'timestamp')


@admin.register(FieldMatrix)
class FieldMatrixAdmin(admin.ModelAdmin):
    list_display = ('field', 'timestamp')



