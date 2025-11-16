from django.contrib import admin
from .models import Equipo, Liga, Partido


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nombre_corto', 'id_api')
    search_fields = ('nombre', 'nombre_corto')
    list_filter = ('nombre',)


@admin.register(Liga)
class LigaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pais', 'id_api')
    search_fields = ('nombre', 'pais')
    list_filter = ('pais',)


@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = ('equipo_local', 'equipo_visitante', 'fecha', 'goles_local', 'goles_visitante', 'estado', 'liga')
    list_filter = ('estado', 'liga', 'fecha')
    search_fields = ('equipo_local__nombre', 'equipo_visitante__nombre')
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha_actualizacion',)

