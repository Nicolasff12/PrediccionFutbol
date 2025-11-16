from django.urls import path
from . import views

app_name = 'partidos'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('sincronizar/', views.sincronizar_partidos_view, name='sincronizar'),
]

