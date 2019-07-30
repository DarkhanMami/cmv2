from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = 'Администрирование'
admin.site.site_title = 'EmirOil'


urlpatterns = [
    path('main/', include('main.urls')),
    # path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('tinymce/', include('tinymce.urls')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),

    # prefix_default_language=False
)