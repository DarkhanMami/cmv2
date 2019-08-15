from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group

from main import models
from main.models import Field, Well, WellMatrix, TS, Depression


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


@admin.register(Well)
class WellAdmin(admin.ModelAdmin):
    list_display = ('field', 'name', 'teh_rej_fluid', 'teh_rej_oil', 'teh_rej_water', 'production_type')
    search_fields = ('name',)
    list_filter = ('field',)


@admin.register(WellMatrix)
class WellMatrixAdmin(admin.ModelAdmin):
    list_display = ('well', 'filling', 'fluid_agzu', 'fluid_isu', 'shortage_isu', 'shortage_prs', 'shortage_wait',
                    'well_stop', 'oil_loss', 'active', 'has_isu', 'performance', 'brigade_num', 'ts_num')
    search_fields = ('well',)


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
