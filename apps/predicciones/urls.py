from django.urls import path
from . import views

app_name = 'predicciones'

urlpatterns = [
    path('', views.mis_predicciones_view, name='mis_predicciones'),
    path('crear/<int:partido_id>/', views.crear_prediccion_view, name='crear'),
    path('detalle/<int:prediccion_id>/', views.detalle_prediccion_view, name='detalle'),
    path('generar-ia/<int:partido_id>/', views.generar_prediccion_ia_ajax, name='generar_ia'),
]

