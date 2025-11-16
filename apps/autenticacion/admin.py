from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'es_activo', 'fecha_registro')
    list_filter = ('es_activo', 'fecha_registro')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-fecha_registro',)

