from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('update_VMB_tags/', views.update_VMB_tags),
]