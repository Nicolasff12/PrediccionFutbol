from django.urls import path
from . import views
from . import api_views

app_name = 'partidos'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('sincronizar/', views.sincronizar_partidos_view, name='sincronizar'),
    # API endpoints
    path('api/home-data/', api_views.HomeDataAPIView.as_view(), name='api_home_data'),
    path('api/comparacion-partido/<int:partido_id>/', api_views.ComparacionPartidoAPIView.as_view(), name='api_comparacion_partido'),
]

