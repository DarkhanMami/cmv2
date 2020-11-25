from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('update_VMB_tags/', views.update_VMB_tags),
    path('update_Prorva_tags/', views.update_Prorva_tags),
    path('update_Kainar_KUUN_tags/', views.update_Kainar_KUUN_tags),
]