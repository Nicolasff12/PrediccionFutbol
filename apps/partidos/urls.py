from django.urls import path
from . import views
from . import api_views

app_name = 'partidos'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('sincronizar/', views.sincronizar_partidos_view, name='sincronizar'),
    path('equipos/', views.lista_equipos_view, name='lista_equipos'),
    path('equipos/<int:equipo_id>/', views.detalle_equipo_view, name='detalle_equipo'),
    path('comparar/', views.comparar_equipos_view, name='comparar_equipos'),
    # API endpoints
    path('api/home-data/', api_views.HomeDataAPIView.as_view(), name='api_home_data'),
    path('api/comparacion-partido/<int:partido_id>/', api_views.ComparacionPartidoAPIView.as_view(), name='api_comparacion_partido'),
]

