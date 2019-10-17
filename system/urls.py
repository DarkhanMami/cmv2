from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
import all_tags.Moldabek.all_tags

admin.site.site_header = 'Администрирование'
admin.site.site_title = 'CM_v2'


urlpatterns = [
    path('main/', include('main.urls')),
    # path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('update_VMB_tags/', all_tags.Moldabek.all_tags),

]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),

    # prefix_default_language=False
)