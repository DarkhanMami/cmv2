from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('update_VMB_tags/', views.update_VMB_tags),
    path('update_VMB_zamer()/', views.update_VMB_zamer()),
    path('update_Prorva_tags/', views.update_Prorva_tags),
    path('update_Kainar_KUUN_tags/', views.update_Kainar_KUUN_tags),
    path('update_UAZ_TM_tags/', views.update_UAZ_TM_tags),
    path('update_UAZ_DRP_tags/', views.update_UAZ_DRP_tags),
]