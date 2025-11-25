"""
Management command para sincronizar datos reales de Besoccer
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.partidos.models import Liga, Equipo, Partido
from apps.partidos.services import BesoccerService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sincroniza datos reales de Besoccer (equipos y partidos)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--crear-partidos-prueba',
            action='store_true',
            help='Crea partidos de prueba basados en los equipos reales',
        )

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('Sincronizando datos de Besoccer...'))
        self.stdout.write('=' * 60)
        
        besoccer_service = BesoccerService()
        
        # 1. Crear o actualizar Liga BetPlay
        self.stdout.write('\n[1/3] Creando/Actualizando Liga BetPlay...')
        liga, created = Liga.objects.get_or_create(
            id_api=50,  # ID de Liga BetPlay en Besoccer
            defaults={
                'nombre': 'Liga BetPlay Dimayor',
                'pais': 'Colombia',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Liga creada: {liga.nombre}'))
        else:
            self.stdout.write(f'  Liga ya existe: {liga.nombre}')
        
        # 2. Obtener equipos reales de Besoccer
        self.stdout.write('\n[2/3] Obteniendo equipos de Besoccer...')
        try:
            equipos_data = besoccer_service.obtener_equipos_liga(league_id=50)
            
            if not equipos_data:
                self.stdout.write(self.style.WARNING('⚠ No se pudieron obtener equipos de Besoccer'))
                self.stdout.write('  Usando datos de prueba...')
                self._crear_equipos_prueba(liga)
            else:
                equipos_creados = 0
                equipos_actualizados = 0
                
                for equipo_data in equipos_data:
                    # Normalizar los datos según la estructura real de la API de Besoccer
                    equipo_id_str = equipo_data.get('id') or equipo_data.get('team_id')
                    if not equipo_id_str:
                        continue
                    
                    try:
                        equipo_id = int(equipo_id_str)
                    except (ValueError, TypeError):
                        continue
                    
                    # La API usa nameShowTeam o nameShow como nombre principal
                    nombre = equipo_data.get('nameShowTeam') or equipo_data.get('nameShow') or equipo_data.get('name') or equipo_data.get('fullName') or ''
                    nombre_corto = equipo_data.get('short_name') or equipo_data.get('short') or ''
                    # La API usa shield o shield_big para el escudo
                    escudo = equipo_data.get('shield_big') or equipo_data.get('shield') or equipo_data.get('logo') or equipo_data.get('image') or ''
                    
                    if not nombre:
                        # Si no hay nombre, usar el fullName o generar uno
                        nombre = equipo_data.get('fullName') or f'Equipo {equipo_id}'
                    
                    if not nombre_corto:
                        # Generar nombre corto desde el nombre
                        nombre_corto = nombre[:3].upper() if len(nombre) >= 3 else nombre.upper()
                    
                    equipo, created = Equipo.objects.update_or_create(
                        id_api=equipo_id,
                        defaults={
                            'nombre': nombre,
                            'nombre_corto': nombre_corto,
                            'escudo': escudo
                        }
                    )
                    
                    if created:
                        equipos_creados += 1
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Equipo creado: {equipo.nombre}'))
                    else:
                        equipos_actualizados += 1
                        self.stdout.write(f'  → Equipo actualizado: {equipo.nombre}')
                
                self.stdout.write(self.style.SUCCESS(
                    f'\n✓ Equipos procesados: {equipos_creados} creados, {equipos_actualizados} actualizados'
                ))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error obteniendo equipos: {e}'))
            self.stdout.write('  Usando datos de prueba...')
            self._crear_equipos_prueba(liga)
        
        # 3. Intentar obtener partidos reales o crear partidos de prueba
        self.stdout.write('\n[3/3] Obteniendo partidos...')
        
        if options['crear_partidos_prueba']:
            self._crear_partidos_prueba(liga)
        else:
            # Intentar obtener partidos reales
            try:
                partidos_data = besoccer_service.obtener_partidos_proximos(limite=20)
                
                if partidos_data:
                    self._procesar_partidos_reales(partidos_data, liga)
                else:
                    self.stdout.write(self.style.WARNING('⚠ No se pudieron obtener partidos reales'))
                    self.stdout.write('  Ejecuta con --crear-partidos-prueba para crear partidos de prueba')
                    
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠ Error obteniendo partidos: {e}'))
                self.stdout.write('  Ejecuta con --crear-partidos-prueba para crear partidos de prueba')
        
        # Resumen final
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('Resumen:'))
        self.stdout.write(f'  - Ligas: {Liga.objects.count()}')
        self.stdout.write(f'  - Equipos: {Equipo.objects.count()}')
        self.stdout.write(f'  - Partidos: {Partido.objects.count()}')
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('\n✓ Sincronización completada!'))
    
    def _crear_equipos_prueba(self, liga):
        """Crea equipos de prueba si no se pueden obtener de la API"""
        equipos_data = [
            {'nombre': 'Millonarios FC', 'nombre_corto': 'MIL', 'id_api': 1},
            {'nombre': 'Atlético Nacional', 'nombre_corto': 'NAC', 'id_api': 2},
            {'nombre': 'América de Cali', 'nombre_corto': 'AME', 'id_api': 3},
            {'nombre': 'Deportivo Cali', 'nombre_corto': 'CAL', 'id_api': 4},
            {'nombre': 'Independiente Santa Fe', 'nombre_corto': 'SFE', 'id_api': 5},
            {'nombre': 'Junior de Barranquilla', 'nombre_corto': 'JUN', 'id_api': 6},
            {'nombre': 'Once Caldas', 'nombre_corto': 'ONC', 'id_api': 7},
            {'nombre': 'Tolima', 'nombre_corto': 'TOL', 'id_api': 8},
        ]
        
        for eq_data in equipos_data:
            equipo, created = Equipo.objects.get_or_create(
                id_api=eq_data['id_api'],
                defaults={
                    'nombre': eq_data['nombre'],
                    'nombre_corto': eq_data['nombre_corto']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Equipo creado: {equipo.nombre}'))
    
    def _procesar_partidos_reales(self, partidos_data, liga):
        """Procesa partidos reales obtenidos de la API"""
        partidos_creados = 0
        partidos_actualizados = 0
        
        for partido_data in partidos_data:
            try:
                # Obtener IDs de equipos
                home_team = partido_data.get('home_team', {})
                away_team = partido_data.get('away_team', {})
                
                if isinstance(home_team, dict):
                    equipo_local_id = home_team.get('id')
                    nombre_local = home_team.get('name', '')
                else:
                    equipo_local_id = partido_data.get('home_team_id')
                    nombre_local = partido_data.get('home_team_name', '')
                
                if isinstance(away_team, dict):
                    equipo_visitante_id = away_team.get('id')
                    nombre_visitante = away_team.get('name', '')
                else:
                    equipo_visitante_id = partido_data.get('away_team_id')
                    nombre_visitante = partido_data.get('away_team_name', '')
                
                # Buscar equipos en la base de datos
                try:
                    equipo_local = Equipo.objects.get(id_api=equipo_local_id)
                except Equipo.DoesNotExist:
                    # Crear equipo si no existe
                    equipo_local = Equipo.objects.create(
                        id_api=equipo_local_id,
                        nombre=nombre_local,
                        nombre_corto=nombre_local[:3].upper() if nombre_local else 'LOC'
                    )
                    self.stdout.write(f'  → Equipo creado: {equipo_local.nombre}')
                
                try:
                    equipo_visitante = Equipo.objects.get(id_api=equipo_visitante_id)
                except Equipo.DoesNotExist:
                    # Crear equipo si no existe
                    equipo_visitante = Equipo.objects.create(
                        id_api=equipo_visitante_id,
                        nombre=nombre_visitante,
                        nombre_corto=nombre_visitante[:3].upper() if nombre_visitante else 'VIS'
                    )
                    self.stdout.write(f'  → Equipo creado: {equipo_visitante.nombre}')
                
                # Procesar fecha
                fecha_str = partido_data.get('date') or partido_data.get('datetime') or partido_data.get('fecha')
                try:
                    from datetime import datetime
                    if 'T' in fecha_str:
                        fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                    else:
                        fecha = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
                except:
                    fecha = timezone.now() + timedelta(days=1)
                
                # Procesar estado
                estado_api = partido_data.get('status') or partido_data.get('estado', 'NS')
                estado = self._mapear_estado(estado_api)
                
                # Procesar goles
                goles_local = partido_data.get('home_score') or partido_data.get('goles_local', 0)
                goles_visitante = partido_data.get('away_score') or partido_data.get('goles_visitante', 0)
                
                # ID del partido en la API
                partido_id_api = partido_data.get('id') or partido_data.get('match_id')
                
                # Crear o actualizar partido
                partido, created = Partido.objects.update_or_create(
                    id_api=partido_id_api,
                    defaults={
                        'equipo_local': equipo_local,
                        'equipo_visitante': equipo_visitante,
                        'liga': liga,
                        'fecha': fecha,
                        'goles_local': goles_local,
                        'goles_visitante': goles_visitante,
                        'estado': estado
                    }
                )
                
                if created:
                    partidos_creados += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Partido creado: {partido.equipo_local.nombre} vs {partido.equipo_visitante.nombre}'
                        )
                    )
                else:
                    partidos_actualizados += 1
                    
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ⚠ Error procesando partido: {e}'))
                continue
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Partidos procesados: {partidos_creados} creados, {partidos_actualizados} actualizados'
        ))
    
    def _crear_partidos_prueba(self, liga):
        """Crea partidos de prueba basados en los equipos existentes"""
        # Solo usar equipos que tengan nombre (equipos reales de Besoccer)
        equipos = list(Equipo.objects.exclude(nombre='').exclude(nombre__isnull=True).filter(nombre__gt=''))
        
        if len(equipos) < 2:
            self.stdout.write(self.style.WARNING('⚠ No hay suficientes equipos para crear partidos'))
            return
        
        self.stdout.write('  Creando partidos de prueba...')
        
        ahora = timezone.now()
        partidos_creados = 0
        
        # Crear partidos próximos
        for i in range(min(8, len(equipos) // 2)):
            equipo_local = equipos[i * 2]
            equipo_visitante = equipos[i * 2 + 1] if (i * 2 + 1) < len(equipos) else equipos[0]
            
            partido, created = Partido.objects.get_or_create(
                equipo_local=equipo_local,
                equipo_visitante=equipo_visitante,
                liga=liga,
                fecha=ahora + timedelta(days=i+1, hours=20),
                defaults={'estado': 'NS'}
            )
            
            if created:
                partidos_creados += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Partido creado: {partido.equipo_local.nombre} vs {partido.equipo_visitante.nombre}'
                    )
                )
        
        # Crear algunos partidos finalizados
        for i in range(min(4, len(equipos) // 2)):
            equipo_local = equipos[i * 2]
            equipo_visitante = equipos[i * 2 + 1] if (i * 2 + 1) < len(equipos) else equipos[0]
            
            partido, created = Partido.objects.get_or_create(
                equipo_local=equipo_local,
                equipo_visitante=equipo_visitante,
                liga=liga,
                fecha=ahora - timedelta(days=i+1),
                defaults={
                    'goles_local': 2 + i,
                    'goles_visitante': 1 + i,
                    'estado': 'FT'
                }
            )
            
            if created:
                partidos_creados += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Partido finalizado creado: {partido.equipo_local.nombre} {partido.goles_local}-{partido.goles_visitante} {partido.equipo_visitante.nombre}'
                    )
                )
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ {partidos_creados} partidos de prueba creados'))
    
    def _mapear_estado(self, estado_api: str) -> str:
        """Mapea el estado de la API al estado del modelo"""
        mapeo = {
            'NS': 'NS',
            'LIVE': 'LIVE',
            'FT': 'FT',
            'POST': 'POST',
            'CANC': 'CANC',
            'finished': 'FT',
            'not_started': 'NS',
            'live': 'LIVE',
            'postponed': 'POST',
            'cancelled': 'CANC'
        }
        return mapeo.get(estado_api, 'NS')

