"""
Servicio para calcular estadísticas desde los datos locales de la base de datos
cuando la API de Besoccer no está disponible
"""
from typing import Dict, Optional, List
from django.db.models import Q, Count, Sum, Avg
from apps.partidos.models import Equipo, Partido, Liga
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class EstadisticasCalculadas:
    """Calcula estadísticas de equipos desde datos locales"""
    
    @staticmethod
    def obtener_estadisticas_equipo(equipo: Equipo, liga: Liga) -> Optional[Dict]:
        """Calcula estadísticas de un equipo desde partidos locales"""
        try:
            # Obtener todos los partidos del equipo en la liga
            partidos = Partido.objects.filter(
                liga=liga
            ).filter(
                Q(equipo_local=equipo) | Q(equipo_visitante=equipo)
            ).filter(estado='FT')  # Solo partidos finalizados
            
            total_partidos = partidos.count()
            
            if total_partidos == 0:
                return None
            
            # Calcular victorias, empates, derrotas
            victorias = 0
            empates = 0
            derrotas = 0
            goles_favor = 0
            goles_contra = 0
            
            # Estadísticas como local
            partidos_local = partidos.filter(equipo_local=equipo)
            victorias_local = 0
            empates_local = 0
            derrotas_local = 0
            goles_favor_local = 0
            goles_contra_local = 0
            
            for partido in partidos_local:
                goles_favor += partido.goles_local
                goles_contra += partido.goles_visitante
                goles_favor_local += partido.goles_local
                goles_contra_local += partido.goles_visitante
                
                if partido.goles_local > partido.goles_visitante:
                    victorias += 1
                    victorias_local += 1
                elif partido.goles_local == partido.goles_visitante:
                    empates += 1
                    empates_local += 1
                else:
                    derrotas += 1
                    derrotas_local += 1
            
            # Estadísticas como visitante
            partidos_visitante = partidos.filter(equipo_visitante=equipo)
            victorias_visitante = 0
            empates_visitante = 0
            derrotas_visitante = 0
            goles_favor_visitante = 0
            goles_contra_visitante = 0
            
            for partido in partidos_visitante:
                goles_favor += partido.goles_visitante
                goles_contra += partido.goles_local
                goles_favor_visitante += partido.goles_visitante
                goles_contra_visitante += partido.goles_local
                
                if partido.goles_visitante > partido.goles_local:
                    victorias += 1
                    victorias_visitante += 1
                elif partido.goles_visitante == partido.goles_local:
                    empates += 1
                    empates_visitante += 1
                else:
                    derrotas += 1
                    derrotas_visitante += 1
            
            # Calcular puntos (3 por victoria, 1 por empate)
            puntos = (victorias * 3) + empates
            
            # Calcular promedios
            promedio_goles_favor = goles_favor / total_partidos if total_partidos > 0 else 0
            promedio_goles_contra = goles_contra / total_partidos if total_partidos > 0 else 0
            
            # Obtener posición en la tabla (si está disponible)
            posicion = EstadisticasCalculadas._obtener_posicion_equipo(equipo, liga)
            
            return {
                'partidos_jugados': total_partidos,
                'victorias': victorias,
                'empates': empates,
                'derrotas': derrotas,
                'puntos': puntos,
                'goles_a_favor': goles_favor,
                'goles_en_contra': goles_contra,
                'diferencia_goles': goles_favor - goles_contra,
                'promedio_goles_favor': round(promedio_goles_favor, 2),
                'promedio_goles_contra': round(promedio_goles_contra, 2),
                'posicion': posicion,
                'estadisticas_local': {
                    'victorias': victorias_local,
                    'empates': empates_local,
                    'derrotas': derrotas_local,
                    'goles_favor': goles_favor_local,
                    'goles_contra': goles_contra_local,
                    'partidos': partidos_local.count()
                },
                'estadisticas_visitante': {
                    'victorias': victorias_visitante,
                    'empates': empates_visitante,
                    'derrotas': derrotas_visitante,
                    'goles_favor': goles_favor_visitante,
                    'goles_contra': goles_contra_visitante,
                    'partidos': partidos_visitante.count()
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculando estadísticas del equipo {equipo.id}: {e}")
            return None
    
    @staticmethod
    def _obtener_posicion_equipo(equipo: Equipo, liga: Liga) -> Optional[int]:
        """Calcula la posición del equipo en la tabla"""
        try:
            # Obtener todos los equipos de la liga con sus estadísticas
            equipos_liga = Equipo.objects.filter(
                partidos_local__liga=liga
            ).distinct() | Equipo.objects.filter(
                partidos_visitante__liga=liga
            ).distinct()
            
            equipos_stats = []
            for eq in equipos_liga:
                stats = EstadisticasCalculadas.obtener_estadisticas_equipo(eq, liga)
                if stats:
                    equipos_stats.append({
                        'equipo': eq,
                        'puntos': stats['puntos'],
                        'diferencia_goles': stats['diferencia_goles'],
                        'goles_favor': stats['goles_a_favor']
                    })
            
            # Ordenar por puntos, diferencia de goles, goles a favor
            equipos_stats.sort(
                key=lambda x: (x['puntos'], x['diferencia_goles'], x['goles_favor']),
                reverse=True
            )
            
            # Encontrar posición del equipo
            for i, eq_stat in enumerate(equipos_stats, 1):
                if eq_stat['equipo'].id == equipo.id:
                    return i
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculando posición del equipo {equipo.id}: {e}")
            return None
    
    @staticmethod
    def obtener_ultimos_partidos_equipo(equipo: Equipo, liga: Liga, limite: int = 5) -> List[Dict]:
        """Obtiene los últimos partidos de un equipo desde la base de datos"""
        try:
            partidos = Partido.objects.filter(
                liga=liga
            ).filter(
                Q(equipo_local=equipo) | Q(equipo_visitante=equipo)
            ).filter(
                estado='FT'
            ).order_by('-fecha')[:limite]
            
            partidos_formateados = []
            for partido in partidos:
                # Determinar si jugó como local o visitante
                condicion = 'local' if partido.equipo_local == equipo else 'visitante'
                
                # Obtener rival y resultado
                if condicion == 'local':
                    rival = partido.equipo_visitante.nombre
                    goles_equipo = partido.goles_local
                    goles_rival = partido.goles_visitante
                else:
                    rival = partido.equipo_local.nombre
                    goles_equipo = partido.goles_visitante
                    goles_rival = partido.goles_local
                
                resultado = f"{goles_equipo}-{goles_rival}"
                fecha = partido.fecha.strftime('%Y-%m-%d') if partido.fecha else ''
                
                partidos_formateados.append({
                    'resultado': resultado,
                    'rival': rival,
                    'fecha': fecha,
                    'condicion': condicion
                })
            
            return partidos_formateados
            
        except Exception as e:
            logger.error(f"Error obteniendo últimos partidos del equipo {equipo.id}: {e}")
            return []
    
    @staticmethod
    def obtener_historial_enfrentamientos(equipo1: Equipo, equipo2: Equipo, liga: Liga, limite: int = 5) -> List[Dict]:
        """Obtiene el historial de enfrentamientos entre dos equipos"""
        try:
            partidos = Partido.objects.filter(
                liga=liga,
                estado='FT'
            ).filter(
                (Q(equipo_local=equipo1) & Q(equipo_visitante=equipo2)) |
                (Q(equipo_local=equipo2) & Q(equipo_visitante=equipo1))
            ).order_by('-fecha')[:limite]
            
            historial = []
            for partido in partidos:
                resultado = f"{partido.goles_local}-{partido.goles_visitante}"
                fecha = partido.fecha.strftime('%Y-%m-%d') if partido.fecha else ''
                historial.append({
                    'resultado': resultado,
                    'fecha': fecha
                })
            
            return historial
            
        except Exception as e:
            logger.error(f"Error obteniendo historial de enfrentamientos: {e}")
            return []
    
    @staticmethod
    def obtener_tabla_posiciones(liga: Liga) -> List[Dict]:
        """Calcula la tabla de posiciones desde datos locales"""
        try:
            # Obtener todos los equipos que han jugado en la liga
            equipos_liga = Equipo.objects.filter(
                partidos_local__liga=liga
            ).distinct() | Equipo.objects.filter(
                partidos_visitante__liga=liga
            ).distinct()
            
            tabla = []
            for equipo in equipos_liga:
                stats = EstadisticasCalculadas.obtener_estadisticas_equipo(equipo, liga)
                if stats and stats['partidos_jugados'] > 0:
                    tabla.append({
                        'equipo': equipo.nombre,
                        'posicion': stats.get('posicion', 0),
                        'puntos': stats['puntos'],
                        'partidos_jugados': stats['partidos_jugados'],
                        'victorias': stats['victorias'],
                        'empates': stats['empates'],
                        'derrotas': stats['derrotas'],
                        'goles_favor': stats['goles_a_favor'],
                        'goles_contra': stats['goles_en_contra'],
                        'diferencia_goles': stats['diferencia_goles']
                    })
            
            # Ordenar por posición
            tabla.sort(key=lambda x: x['posicion'])
            
            return tabla
            
        except Exception as e:
            logger.error(f"Error calculando tabla de posiciones: {e}")
            return []

