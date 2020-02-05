# api/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'well_matrix', views.WellMatrixViewSet, base_name='well_matrix')
router.register(r'depression', views.DepressionViewSet, base_name='depression')
router.register(r'fields', views.FieldViewSet, base_name='fields')
router.register(r'wells', views.WellViewSet, base_name='wells')
router.register(r'ts', views.TSViewSet, base_name='ts')
router.register(r'gsm', views.GSMViewSet, base_name='gsm')
router.register(r'prodProfile', views.ProdProfileViewSet, base_name='prodProfile')
router.register(r'imbalance', views.ImbalanceViewSet, base_name='imbalance')


urlpatterns = [
    path('authenticate/', views.AuthView.as_view()),
    path('get_2hour/', views.get_2hour),
    path('upload_dyn_data/', views.upload_dyn_data),
    path('get_dyn_data/', views.get_dyn_data),
    path('update_imbalance/', views.update_imbalance),
    path('update_wells/', views.update_wells),
    path('update_matrix/', views.update_matrix),
    path('update_sum_well/', views.update_sum_well),
    path('imbalance_history_all/', views.ImbalanceHistoryAll.as_view()),
    path('sum_well_in_field/',views.SumWellInFieldSerializerAll.as_view()),
    path('', include(router.urls)),

    path('<int:pk>/', views.DetailUser.as_view()),
    path('rest-auth/', include('rest_auth.urls')),
]