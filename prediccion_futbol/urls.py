"""
URL configuration for prediccion_futbol project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.partidos.urls')),  # Redirige la raíz a partidos
    path('auth/', include('apps.autenticacion.urls')),
    path('predicciones/', include('apps.predicciones.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # En desarrollo, servir desde STATICFILES_DIRS
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()

