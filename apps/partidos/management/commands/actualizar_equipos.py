"""
Management command para actualizar equipos existentes con nombres y escudos
"""
from django.core.management.base import BaseCommand
from apps.partidos.models import Equipo
from apps.partidos.services import BesoccerService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Actualiza equipos existentes con nombres y escudos desde la API de Besoccer'

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('Actualizando equipos desde Besoccer...'))
        self.stdout.write('=' * 60)
        
        besoccer_service = BesoccerService()
        
        # Obtener todos los equipos de la API
        try:
            equipos_data = besoccer_service.obtener_equipos_liga(league_id=50)
            
            if not equipos_data:
                self.stdout.write(self.style.ERROR('No se pudieron obtener equipos de la API'))
                return
            
            self.stdout.write(f'\nObtenidos {len(equipos_data)} equipos de la API')
            
            actualizados = 0
            sin_cambios = 0
            
            for equipo_data in equipos_data:
                equipo_id_str = equipo_data.get('id') or equipo_data.get('team_id')
                if not equipo_id_str:
                    continue
                
                try:
                    equipo_id = int(equipo_id_str)
                except (ValueError, TypeError):
                    continue
                
                # Obtener nombre y escudo
                nombre = equipo_data.get('nameShowTeam') or equipo_data.get('nameShow') or equipo_data.get('name') or equipo_data.get('fullName') or ''
                escudo = equipo_data.get('shield_big') or equipo_data.get('shield') or equipo_data.get('logo') or equipo_data.get('image') or ''
                
                if not nombre or nombre.strip() == '':
                    nombre = equipo_data.get('fullName') or f'Equipo {equipo_id}'
                
                nombre = nombre.strip() if nombre else f'Equipo {equipo_id}'
                
                # Buscar equipo en la BD
                try:
                    equipo = Equipo.objects.get(id_api=equipo_id)
                    
                    # Actualizar si está vacío o diferente
                    actualizado = False
                    if not equipo.nombre or equipo.nombre.strip() == '':
                        equipo.nombre = nombre
                        actualizado = True
                    
                    if escudo and (not equipo.escudo or equipo.escudo.strip() == ''):
                        equipo.escudo = escudo
                        actualizado = True
                    
                    if actualizado:
                        equipo.save()
                        actualizados += 1
                        self.stdout.write(self.style.SUCCESS(f'  [OK] Actualizado: {equipo.nombre}'))
                    else:
                        sin_cambios += 1
                        
                except Equipo.DoesNotExist:
                    # Crear equipo si no existe
                    nombre_corto = equipo_data.get('short_name') or nombre[:3].upper() if len(nombre) >= 3 else nombre.upper()
                    equipo = Equipo.objects.create(
                        id_api=equipo_id,
                        nombre=nombre,
                        nombre_corto=nombre_corto,
                        escudo=escudo if escudo else None
                    )
                    actualizados += 1
                    self.stdout.write(self.style.SUCCESS(f'  [OK] Creado: {equipo.nombre}'))
            
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.SUCCESS(f'Resumen:'))
            self.stdout.write(f'  - Equipos actualizados/creados: {actualizados}')
            self.stdout.write(f'  - Equipos sin cambios: {sin_cambios}')
            self.stdout.write('=' * 60)
            self.stdout.write(self.style.SUCCESS('\n[OK] Actualizacion completada!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            logger.error(f"Error actualizando equipos: {e}", exc_info=True)

