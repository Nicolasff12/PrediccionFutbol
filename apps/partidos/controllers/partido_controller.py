"""
Controlador para manejar la lógica de negocio de partidos
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from apps.partidos.models import Partido, Equipo, Liga
from apps.partidos.services import BesoccerService
import logging

logger = logging.getLogger(__name__)


class PartidoController:
    """Controlador para gestionar partidos"""
    
    def __init__(self):
        self.besoccer_service = BesoccerService()
    
    def sincronizar_liga_betplay(self) -> bool:
        """Sincroniza los datos de la Liga BetPlay desde la API"""
        try:
            # Obtener información de la liga
            liga_data = self.besoccer_service.obtener_liga_betplay()
            if not liga_data:
                logger.warning("No se encontró la Liga BetPlay en la API")
                return False
            
            # Crear o actualizar la liga
            liga, created = Liga.objects.update_or_create(
                id_api=liga_data.get('id'),
                defaults={
                    'nombre': liga_data.get('name', 'Liga BetPlay'),
                    'pais': liga_data.get('country', 'Colombia'),
                    'logo': liga_data.get('logo', '')
                }
            )
            
            # Obtener equipos de la liga
            equipos_data = self.besoccer_service.obtener_equipos_liga(liga_data.get('id'))
            equipos_dict = {}
            
            for equipo_data in equipos_data:
                equipo, _ = Equipo.objects.update_or_create(
                    id_api=equipo_data.get('id'),
                    defaults={
                        'nombre': equipo_data.get('name', ''),
                        'nombre_corto': equipo_data.get('short_name', ''),
                        'escudo': equipo_data.get('logo', '')
                    }
                )
                equipos_dict[equipo_data.get('id')] = equipo
            
            # Obtener partidos próximos (próximos 30 días)
            partidos_data = self.besoccer_service.obtener_partidos_proximos(liga_data.get('id'), dias=30)
            
            for partido_data in partidos_data:
                equipo_local_id = partido_data.get('home_team', {}).get('id')
                equipo_visitante_id = partido_data.get('away_team', {}).get('id')
                
                if equipo_local_id in equipos_dict and equipo_visitante_id in equipos_dict:
                    fecha_str = partido_data.get('date', '')
                    try:
                        fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                    except:
                        fecha = datetime.now()
                    
                    estado = self._mapear_estado(partido_data.get('status', 'NS'))
                    
                    Partido.objects.update_or_create(
                        id_api=partido_data.get('id'),
                        defaults={
                            'equipo_local': equipos_dict[equipo_local_id],
                            'equipo_visitante': equipos_dict[equipo_visitante_id],
                            'liga': liga,
                            'fecha': fecha,
                            'goles_local': partido_data.get('home_score', 0),
                            'goles_visitante': partido_data.get('away_score', 0),
                            'estado': estado
                        }
                    )
            
            logger.info(f"Sincronización completada: {len(partidos_data)} partidos")
            return True
            
        except Exception as e:
            logger.error(f"Error en sincronización: {e}")
            return False
    
    def _mapear_estado(self, estado_api: str) -> str:
        """Mapea el estado de la API al estado del modelo"""
        mapeo = {
            'NS': 'NS',
            'LIVE': 'LIVE',
            'FT': 'FT',
            'POST': 'POST',
            'CANC': 'CANC'
        }
        return mapeo.get(estado_api, 'NS')
    
    def obtener_partidos_proximos(self, limite: int = 10) -> List[Partido]:
        """Obtiene los próximos partidos desde la base de datos"""
        ahora = datetime.now()
        return Partido.objects.filter(
            fecha__gte=ahora,
            estado__in=['NS', 'LIVE']
        ).select_related('equipo_local', 'equipo_visitante', 'liga').order_by('fecha')[:limite]
    
    def obtener_partidos_recientes(self, limite: int = 10) -> List[Partido]:
        """Obtiene los partidos recientes finalizados"""
        return Partido.objects.filter(
            estado='FT'
        ).select_related('equipo_local', 'equipo_visitante', 'liga').order_by('-fecha')[:limite]
    
    def obtener_partidos_hoy(self) -> List[Partido]:
        """Obtiene los partidos del día actual"""
        hoy = datetime.now().date()
        return Partido.objects.filter(
            fecha__date=hoy
        ).select_related('equipo_local', 'equipo_visitante', 'liga').order_by('fecha')
    
    def obtener_estadisticas_liga(self) -> Dict:
        """Obtiene estadísticas generales de la liga"""
        total_partidos = Partido.objects.count()
        partidos_finalizados = Partido.objects.filter(estado='FT').count()
        partidos_proximos = Partido.objects.filter(estado='NS').count()
        partidos_en_vivo = Partido.objects.filter(estado='LIVE').count()
        
        return {
            'total_partidos': total_partidos,
            'partidos_finalizados': partidos_finalizados,
            'partidos_proximos': partidos_proximos,
            'partidos_en_vivo': partidos_en_vivo
        }

