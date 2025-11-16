from django.contrib import admin
from .models import Prediccion


@admin.register(Prediccion)
class PrediccionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'partido', 'goles_local_predicho', 'goles_visitante_predicho', 'confianza', 'es_correcta', 'fecha_prediccion')
    list_filter = ('es_correcta', 'fecha_prediccion', 'confianza')
    search_fields = ('usuario__username', 'partido__equipo_local__nombre', 'partido__equipo_visitante__nombre')
    readonly_fields = ('fecha_prediccion',)
    date_hierarchy = 'fecha_prediccion'

