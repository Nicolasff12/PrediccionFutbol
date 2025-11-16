from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'auth'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

