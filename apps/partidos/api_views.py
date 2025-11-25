"""
Vistas API para obtener datos del HOME y comparación de partidos
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json
from typing import Dict, List
from datetime import datetime, timedelta
from .services import BesoccerService
# from .services import EstadisticasCalculadas  # Deshabilitado temporalmente
from .models import Liga, Equipo, Partido
from .controllers import PartidoController
from .utils import calcular_estadisticas_equipo, calcular_forma_equipo, calcular_probabilidades_partido
import logging

logger = logging.getLogger(__name__)

besoccer_service = BesoccerService()
partido_controller = PartidoController()


def _calcular_forma_equipo(partidos: List[Dict], equipo_id: int) -> str:
    """Calcula la forma de un equipo (últimos 5 resultados)"""
    forma = []
    for partido in partidos[:5]:
        if partido.get('status') != 'FT':
            continue
        
        es_local = partido.get('home_team', {}).get('id') == equipo_id
        goles_local = partido.get('home_score', 0)
        goles_visitante = partido.get('away_score', 0)
        
        if es_local:
            if goles_local > goles_visitante:
                forma.append('W')
            elif goles_local < goles_visitante:
                forma.append('L')
            else:
                forma.append('D')
        else:
            if goles_visitante > goles_local:
                forma.append('W')
            elif goles_visitante < goles_local:
                forma.append('L')
            else:
                forma.append('D')
    
    return ''.join(forma) if forma else 'N/A'


def _calcular_probabilidades_rapidas(equipo_local_id: int, equipo_visitante_id: int, 
                                     competition_id: str = None) -> Dict[str, float]:
    """Calcula probabilidades rápidas basadas en estadísticas"""
    try:
        # Obtener estadísticas de ambos equipos
        stats_local = besoccer_service.obtener_estadisticas_equipo_detalladas(equipo_local_id, competition_id)
        stats_visitante = besoccer_service.obtener_estadisticas_equipo_detalladas(equipo_visitante_id, competition_id)
        
        # Obtener tabla de posiciones
        tabla = besoccer_service.obtener_tabla_posiciones(competition_id)
        
        pos_local = next((t for t in tabla if t.get('team_id') == equipo_local_id), {})
        pos_visitante = next((t for t in tabla if t.get('team_id') == equipo_visitante_id), {})
        
        puntos_local = pos_local.get('points', 0)
        puntos_visitante = pos_visitante.get('points', 0)
        total_puntos = puntos_local + puntos_visitante
        
        if total_puntos > 0:
            prob_local = (puntos_local / total_puntos) * 0.6 + 0.2  # Sesgo hacia local
            prob_visitante = (puntos_visitante / total_puntos) * 0.6 + 0.1
            prob_empate = 0.3 - (abs(puntos_local - puntos_visitante) / total_puntos) * 0.2
        else:
            prob_local = 0.4
            prob_visitante = 0.3
            prob_empate = 0.3
        
        # Normalizar
        total = prob_local + prob_visitante + prob_empate
        return {
            'local': round((prob_local / total) * 100, 1),
            'empate': round((prob_empate / total) * 100, 1),
            'visitante': round((prob_visitante / total) * 100, 1)
        }
    except Exception as e:
        logger.error(f"Error calculando probabilidades: {e}")
        return {'local': 40.0, 'empate': 30.0, 'visitante': 30.0}


@method_decorator(login_required, name='dispatch')
class HomeDataAPIView(View):
    """API para obtener todos los datos del HOME"""
    
    def get(self, request):
        try:
            # Obtener liga BetPlay
            liga_betplay = Liga.objects.filter(id_api__isnull=False).first()
            if not liga_betplay:
                # Intentar obtener equipos directamente de la API para mostrar algo
                logger.info("Liga no encontrada en BD, intentando obtener equipos de la API...")
                # Usar el default del servicio (Liga Colombia - 50)
                equipos_api = besoccer_service.obtener_equipos_liga()
                if equipos_api:
                    # Formatear equipos para mostrar
                    equipos_formateados = []
                    for equipo in equipos_api[:20]:  # Mostrar más equipos
                        equipos_formateados.append({
                            'id': equipo.get('id'),
                            'nombre': equipo.get('nameShow', equipo.get('fullName', 'N/A')),
                            'escudo': equipo.get('shield', equipo.get('shield_big', '')),
                            'nombre_corto': equipo.get('short_name', ''),
                            'fullName': equipo.get('fullName', '')
                        })
                    
                    return JsonResponse({
                        'proximos_partidos': [],
                        'tabla_posiciones': [],
                        'equipos_destacados': {},
                        'estadisticas_globales': {},
                        'equipos_disponibles': equipos_formateados,
                        'info': 'Equipos disponibles desde la API de BeSoccer. Para ver partidos y tabla de posiciones, sincroniza los partidos desde el botón "Sincronizar Partidos".',
                        'liga_id_api': 50  # Liga Colombia
                    })
                return JsonResponse({
                    'error': 'Liga no encontrada. Por favor sincroniza los partidos primero.',
                    'proximos_partidos': [],
                    'tabla_posiciones': [],
                    'equipos_destacados': {},
                    'estadisticas_globales': {}
                }, status=200)
            
            # Usar competition_id en lugar de liga_id
            competition_id = liga_betplay.id_api if liga_betplay else None
            # Si no hay liga, usar el default
            if not competition_id:
                competition_id = 'colombia_primera_a'
            
            # A. Próximos partidos
            proximos_partidos = self._obtener_proximos_partidos(competition_id)
            
            # B. Tabla de posiciones
            tabla_posiciones = self._obtener_tabla_posiciones(competition_id)
            
            # Si no hay datos, intentar mostrar equipos disponibles
            if not proximos_partidos and not tabla_posiciones:
                equipos_api = besoccer_service.obtener_equipos_liga(league_id=50)  # Liga Colombia
                if equipos_api:
                    equipos_formateados = []
                    for equipo in equipos_api[:20]:
                        equipos_formateados.append({
                            'id': equipo.get('id'),
                            'nombre': equipo.get('nameShow', equipo.get('fullName', 'N/A')),
                            'escudo': equipo.get('shield', equipo.get('shield_big', '')),
                            'nombre_corto': equipo.get('short_name', ''),
                            'fullName': equipo.get('fullName', '')
                        })
                    
                    return JsonResponse({
                        'proximos_partidos': [],
                        'tabla_posiciones': [],
                        'equipos_destacados': {},
                        'estadisticas_globales': {},
                        'equipos_disponibles': equipos_formateados,
                        'info': 'Equipos disponibles desde la API de BeSoccer. Para ver partidos y tabla de posiciones, sincroniza los partidos desde el botón "Sincronizar Partidos".',
                        'liga_id_api': 50  # Liga Colombia
                    })
            
            # C. Equipos destacados
            equipos_destacados = self._obtener_equipos_destacados(competition_id, tabla_posiciones)
            
            # D. Estadísticas globales
            estadisticas_globales = self._obtener_estadisticas_globales(competition_id, tabla_posiciones)
            
            return JsonResponse({
                'proximos_partidos': proximos_partidos,
                'tabla_posiciones': tabla_posiciones,
                'equipos_destacados': equipos_destacados,
                'estadisticas_globales': estadisticas_globales
            })
        except Exception as e:
            logger.error(f"Error en HomeDataAPIView: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    def _obtener_proximos_partidos(self, competition_id: str) -> List[Dict]:
        """Obtiene próximos partidos con todos los detalles"""
        # Intentar obtener de la API, si falla usar base de datos local
        partidos_data = besoccer_service.obtener_partidos_proximos(competition_id, limite=10)
        
        # Si no hay datos de la API, usar base de datos local
        if not partidos_data:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            # Buscar partidos futuros
            partidos_db = Partido.objects.filter(
                fecha__gte=now,
                estado='NS'
            ).select_related('equipo_local', 'equipo_visitante', 'liga').order_by('fecha')[:10]
            
            proximos = []
            for partido in partidos_db:
                # Calcular forma de los equipos
                forma_local = calcular_forma_equipo(partido.equipo_local, partido.liga, 5)
                forma_visitante = calcular_forma_equipo(partido.equipo_visitante, partido.liga, 5)
                
                # Calcular probabilidades basadas en estadísticas históricas
                probabilidades = calcular_probabilidades_partido(partido)
                
                # Obtener estadísticas para mostrar (usar utils, NO EstadisticasCalculadas por ahora)
                stats_local = None
                stats_visitante = None
                try:
                    stats_local = calcular_estadisticas_equipo(partido.equipo_local, partido.liga)
                    stats_visitante = calcular_estadisticas_equipo(partido.equipo_visitante, partido.liga)
                except Exception as e:
                    logger.warning(f"Error calculando estadísticas: {e}")
                    stats_local = {}
                    stats_visitante = {}
                
                proximos.append({
                    'id': partido.id,
                    'id_api': partido.id_api,
                    'equipo_local': {
                        'id': partido.equipo_local.id_api if partido.equipo_local else None,
                        'nombre': partido.equipo_local.nombre if partido.equipo_local else '',
                        'escudo': partido.equipo_local.escudo if partido.equipo_local else '',
                        'forma': forma_local,
                        'posicion': stats_local.get('posicion') if stats_local else None,
                        'estadisticas': {
                            'victorias': stats_local.get('victorias', 0) if stats_local else 0,
                            'empates': stats_local.get('empates', 0) if stats_local else 0,
                            'derrotas': stats_local.get('derrotas', 0) if stats_local else 0,
                            'goles_favor': stats_local.get('goles_a_favor', stats_local.get('goles_favor', 0)) if stats_local else 0,
                            'goles_contra': stats_local.get('goles_en_contra', stats_local.get('goles_contra', 0)) if stats_local else 0,
                            'promedio_goles_favor': stats_local.get('promedio_goles_favor', 0) if stats_local else 0,
                            'puntos': stats_local.get('puntos', 0) if stats_local else 0,
                        }
                    },
                    'equipo_visitante': {
                        'id': partido.equipo_visitante.id_api if partido.equipo_visitante else None,
                        'nombre': partido.equipo_visitante.nombre if partido.equipo_visitante else '',
                        'escudo': partido.equipo_visitante.escudo if partido.equipo_visitante else '',
                        'forma': forma_visitante,
                        'posicion': stats_visitante.get('posicion') if stats_visitante else None,
                        'estadisticas': {
                            'victorias': stats_visitante.get('victorias', 0) if stats_visitante else 0,
                            'empates': stats_visitante.get('empates', 0) if stats_visitante else 0,
                            'derrotas': stats_visitante.get('derrotas', 0) if stats_visitante else 0,
                            'goles_favor': stats_visitante.get('goles_a_favor', stats_visitante.get('goles_favor', 0)) if stats_visitante else 0,
                            'goles_contra': stats_visitante.get('goles_en_contra', stats_visitante.get('goles_contra', 0)) if stats_visitante else 0,
                            'promedio_goles_favor': stats_visitante.get('promedio_goles_favor', 0) if stats_visitante else 0,
                            'puntos': stats_visitante.get('puntos', 0) if stats_visitante else 0,
                        }
                    },
                    'fecha': partido.fecha.strftime('%Y-%m-%d') if partido.fecha else '',
                    'hora': partido.fecha.strftime('%H:%M') if partido.fecha else '',
                    'estadio': getattr(partido, 'estadio', None) or 'Estadio por confirmar',
                    'probabilidades': probabilidades
                })
            return proximos
        
        proximos = []
        for partido_data in partidos_data:
            equipo_local_id = partido_data.get('home_team', {}).get('id')
            equipo_visitante_id = partido_data.get('away_team', {}).get('id')
            
            if not equipo_local_id or not equipo_visitante_id:
                continue
            
            # Obtener forma de los equipos
            partidos_local = besoccer_service.obtener_ultimos_partidos_equipo(equipo_local_id, 5)
            partidos_visitante = besoccer_service.obtener_ultimos_partidos_equipo(equipo_visitante_id, 5)
            
            forma_local = _calcular_forma_equipo(partidos_local, equipo_local_id)
            forma_visitante = _calcular_forma_equipo(partidos_visitante, equipo_visitante_id)
            
            # Obtener mini tabla de posiciones
            tabla = besoccer_service.obtener_tabla_posiciones(competition_id)
            pos_local = next((t for t in tabla if t.get('team_id') == equipo_local_id), {})
            pos_visitante = next((t for t in tabla if t.get('team_id') == equipo_visitante_id), {})
            
            # Calcular probabilidades (usar competition_id como string o None)
            probabilidades = _calcular_probabilidades_rapidas(equipo_local_id, equipo_visitante_id, competition_id)
            
            # Buscar el partido en la base de datos para obtener el ID local
            partido_db = None
            try:
                partido_db = Partido.objects.get(id_api=partido_data.get('id'))
            except Partido.DoesNotExist:
                pass
            
            proximos.append({
                'id': partido_db.id if partido_db else None,
                'id_api': partido_data.get('id'),
                'equipo_local': {
                    'id': equipo_local_id,
                    'nombre': partido_data.get('home_team', {}).get('name', ''),
                    'escudo': partido_data.get('home_team', {}).get('logo', ''),
                    'forma': forma_local,
                    'posicion': pos_local.get('position', 0),
                    'puntos': pos_local.get('points', 0)
                },
                'equipo_visitante': {
                    'id': equipo_visitante_id,
                    'nombre': partido_data.get('away_team', {}).get('name', ''),
                    'escudo': partido_data.get('away_team', {}).get('logo', ''),
                    'forma': forma_visitante,
                    'posicion': pos_visitante.get('position', 0),
                    'puntos': pos_visitante.get('points', 0)
                },
                'fecha': partido_data.get('date', ''),
                'hora': partido_data.get('time', ''),
                'estadio': partido_data.get('venue', {}).get('name', 'N/A') if isinstance(partido_data.get('venue'), dict) else partido_data.get('venue', 'N/A'),
                'probabilidades': probabilidades
            })
        
        return proximos
    
    def _obtener_tabla_posiciones(self, competition_id: str) -> List[Dict]:
        """Obtiene la tabla de posiciones (intenta API primero, luego calcula desde BD local)"""
        # Intentar obtener de la API
        tabla_data = besoccer_service.obtener_tabla_posiciones(competition_id)
        
        # Si hay datos de la API, procesarlos
        if tabla_data:
            tabla = []
            for item in tabla_data:
                # Calcular racha
                equipo_id = item.get('team_id')
                ultimos_partidos = besoccer_service.obtener_ultimos_partidos_equipo(equipo_id, 5)
                racha = _calcular_forma_equipo(ultimos_partidos, equipo_id)
                
                tabla.append({
                    'posicion': item.get('position', 0),
                    'equipo': {
                        'id': equipo_id,
                        'nombre': item.get('team_name', ''),
                        'escudo': item.get('team_logo', '')
                    },
                    'puntos': item.get('points', 0),
                    'pj': item.get('played', 0),
                    'pg': item.get('won', 0),
                    'pe': item.get('drawn', 0),
                    'pp': item.get('lost', 0),
                    'gf': item.get('goals_for', 0),
                    'gc': item.get('goals_against', 0),
                    'dg': item.get('goal_difference', 0),
                    'racha': racha
                })
            return tabla
        
        # Si no hay datos de la API, NO calcular desde base de datos local (deshabilitado temporalmente)
        # try:
        #     liga = Liga.objects.filter(id_api__isnull=False).first()
        #     if not liga:
        #         liga = Liga.objects.first()
        #     
        #     if liga:
        #         tabla_calculada = EstadisticasCalculadas.obtener_tabla_posiciones(liga)
        #         # ... resto del código deshabilitado
        # except Exception as e:
        #     logger.warning(f"Error calculando tabla de posiciones: {e}")
        
        return []
    
    def _obtener_equipos_destacados(self, competition_id: str, tabla: List[Dict]) -> Dict:
        """Obtiene equipos destacados"""
        equipos_destacados = {
            'mejor_racha': None,
            'mas_goleador': None,
            'mas_solido': None,
            'jugador_destacado': None
        }
        
        if not tabla:
            return equipos_destacados
        
        # Mejor racha (más W consecutivos)
        mejor_racha_equipo = max(tabla, key=lambda x: x['racha'].count('W') if x['racha'] != 'N/A' else 0)
        equipos_destacados['mejor_racha'] = {
            'equipo': mejor_racha_equipo['equipo'],
            'racha': mejor_racha_equipo['racha']
        }
        
        # Más goleador
        mas_goleador = max(tabla, key=lambda x: x['gf'])
        equipos_destacados['mas_goleador'] = {
            'equipo': mas_goleador['equipo'],
            'goles': mas_goleador['gf']
        }
        
        # Más sólido defensivamente (menos goles recibidos)
        mas_solido = min(tabla, key=lambda x: x['gc'])
        equipos_destacados['mas_solido'] = {
            'equipo': mas_solido['equipo'],
            'goles_recibidos': mas_solido['gc']
        }
        
        # Jugador destacado (top scorer)
        goleadores = besoccer_service.obtener_goleadores_liga(competition_id, limite=1)
        if goleadores:
            jugador = goleadores[0]
            equipos_destacados['jugador_destacado'] = {
                'nombre': jugador.get('player_name', ''),
                'equipo': jugador.get('team_name', ''),
                'goles': jugador.get('goals', 0)
            }
        
        return equipos_destacados
    
    def _obtener_estadisticas_globales(self, competition_id: str, tabla: List[Dict]) -> Dict:
        """Obtiene estadísticas globales del torneo"""
        if not tabla:
            # NO calcular desde BD local (deshabilitado temporalmente)
            return {}
        
        # Calcular promedio de goles por partido
        total_goles = sum(item['gf'] for item in tabla)
        total_partidos = sum(item['pj'] for item in tabla)
        promedio_goles = round(total_goles / total_partidos, 2) if total_partidos > 0 else 0
        
        # Equipo con más goles
        mas_goles = max(tabla, key=lambda x: x['gf'])
        
        # Equipo con menos goles recibidos
        menos_goles_recibidos = min(tabla, key=lambda x: x['gc'])
        
        # Máximo goleador (intentar desde API, si no está disponible será None)
        goleadores = besoccer_service.obtener_goleadores_liga(competition_id, limite=1)
        max_goleador = None
        if goleadores:
            max_goleador = {
                'nombre': goleadores[0].get('player_name', ''),
                'equipo': goleadores[0].get('team_name', ''),
                'goles': goleadores[0].get('goals', 0)
            }
        
        # Próxima fecha (intentar desde API, si no desde BD local)
        proximos = besoccer_service.obtener_partidos_proximos(competition_id, limite=1)
        proxima_fecha = None
        if proximos:
            fecha_str = proximos[0].get('date', '')
            proxima_fecha = {
                'fecha': fecha_str,
                'partidos': len(proximos)
            }
        else:
            # Buscar en BD local
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            proximo_partido = Partido.objects.filter(
                fecha__gte=now,
                estado='NS'
            ).order_by('fecha').first()
            if proximo_partido:
                proxima_fecha = {
                    'fecha': proximo_partido.fecha.strftime('%Y-%m-%d'),
                    'partidos': Partido.objects.filter(
                        fecha__date=proximo_partido.fecha.date(),
                        estado='NS'
                    ).count()
                }
        
        return {
            'promedio_goles_por_partido': promedio_goles,
            'equipo_mas_goles': {
                'equipo': mas_goles['equipo'],
                'goles': mas_goles['gf']
            },
            'equipo_menos_goles_recibidos': {
                'equipo': menos_goles_recibidos['equipo'],
                'goles': menos_goles_recibidos['gc']
            },
            'maximo_goleador': max_goleador,
            'proxima_fecha': proxima_fecha
        }


@method_decorator(login_required, name='dispatch')
class ComparacionPartidoAPIView(View):
    """API para obtener datos de comparación de un partido específico"""
    
    def get(self, request, partido_id):
        try:
            partido = Partido.objects.select_related('equipo_local', 'equipo_visitante', 'liga').get(id=partido_id)
            
            liga_id = partido.liga.id_api
            equipo_local_id = partido.equipo_local.id_api
            equipo_visitante_id = partido.equipo_visitante.id_api
            
            # A. Datos del partido
            datos_partido = self._obtener_datos_partido(partido)
            
            # B. Datos recientes
            datos_recientes = self._obtener_datos_recientes(equipo_local_id, equipo_visitante_id)
            
            # C. Datos de la temporada
            datos_temporada = self._obtener_datos_temporada(equipo_local_id, equipo_visitante_id, liga_id)
            
            # D. Datos individuales de jugadores
            datos_jugadores = self._obtener_datos_jugadores(equipo_local_id, equipo_visitante_id)
            
            return JsonResponse({
                'datos_partido': datos_partido,
                'datos_recientes': datos_recientes,
                'datos_temporada': datos_temporada,
                'datos_jugadores': datos_jugadores
            })
        except Partido.DoesNotExist:
            return JsonResponse({'error': 'Partido no encontrado'}, status=404)
        except Exception as e:
            logger.error(f"Error en ComparacionPartidoAPIView: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    def _obtener_datos_partido(self, partido: Partido) -> Dict:
        """Obtiene datos básicos del partido"""
        return {
            'equipo_local': {
                'id': partido.equipo_local.id,
                'nombre': partido.equipo_local.nombre,
                'escudo': partido.equipo_local.escudo
            },
            'equipo_visitante': {
                'id': partido.equipo_visitante.id,
                'nombre': partido.equipo_visitante.nombre,
                'escudo': partido.equipo_visitante.escudo
            },
            'fecha': partido.fecha.isoformat(),
            'estadio': 'N/A',  # Se puede obtener de la API si está disponible
            'liga': partido.liga.nombre
        }
    
    def _obtener_datos_recientes(self, equipo_local_id: int, equipo_visitante_id: int) -> Dict:
        """Obtiene datos recientes de ambos equipos"""
        # Últimos 10 partidos de cada equipo
        partidos_local = besoccer_service.obtener_ultimos_partidos_equipo(equipo_local_id, 10)
        partidos_visitante = besoccer_service.obtener_ultimos_partidos_equipo(equipo_visitante_id, 10)
        
        # Partidos como local
        partidos_local_casa = besoccer_service.obtener_partidos_equipo_local(equipo_local_id, 5)
        
        # Partidos como visitante
        partidos_visitante_fuera = besoccer_service.obtener_partidos_equipo_visitante(equipo_visitante_id, 5)
        
        def calcular_estadisticas(partidos, equipo_id):
            victorias = empates = derrotas = 0
            goles_favor = goles_contra = 0
            
            for partido in partidos:
                if partido.get('status') != 'FT':
                    continue
                
                es_local = partido.get('home_team', {}).get('id') == equipo_id
                goles_local = partido.get('home_score', 0)
                goles_visitante = partido.get('away_score', 0)
                
                if es_local:
                    goles_favor += goles_local
                    goles_contra += goles_visitante
                    if goles_local > goles_visitante:
                        victorias += 1
                    elif goles_local < goles_visitante:
                        derrotas += 1
                    else:
                        empates += 1
                else:
                    goles_favor += goles_visitante
                    goles_contra += goles_local
                    if goles_visitante > goles_local:
                        victorias += 1
                    elif goles_visitante < goles_local:
                        derrotas += 1
                    else:
                        empates += 1
            
            return {
                'victorias': victorias,
                'empates': empates,
                'derrotas': derrotas,
                'goles_favor': goles_favor,
                'goles_contra': goles_contra
            }
        
        return {
            'equipo_local': {
                'ultimos_10': calcular_estadisticas(partidos_local, equipo_local_id),
                'como_local': calcular_estadisticas(partidos_local_casa, equipo_local_id)
            },
            'equipo_visitante': {
                'ultimos_10': calcular_estadisticas(partidos_visitante, equipo_visitante_id),
                'como_visitante': calcular_estadisticas(partidos_visitante_fuera, equipo_visitante_id)
            }
        }
    
    def _obtener_datos_temporada(self, equipo_local_id: int, equipo_visitante_id: int, liga_id: int) -> Dict:
        """Obtiene datos de la temporada para ambos equipos"""
        tabla = besoccer_service.obtener_tabla_posiciones(liga_id)
        
        pos_local = next((t for t in tabla if t.get('team_id') == equipo_local_id), {})
        pos_visitante = next((t for t in tabla if t.get('team_id') == equipo_visitante_id), {})
        
        stats_local = besoccer_service.obtener_estadisticas_equipo_detalladas(equipo_local_id, liga_id)
        stats_visitante = besoccer_service.obtener_estadisticas_equipo_detalladas(equipo_visitante_id, liga_id)
        
        def procesar_estadisticas(posicion, stats):
            pj = posicion.get('played', 0)
            return {
                'posicion': posicion.get('position', 0),
                'puntos': posicion.get('points', 0),
                'pj': pj,
                'pg': posicion.get('won', 0),
                'pe': posicion.get('drawn', 0),
                'pp': posicion.get('lost', 0),
                'dg': posicion.get('goal_difference', 0),
                'promedio_goles_por_partido': round(posicion.get('goals_for', 0) / pj, 2) if pj > 0 else 0,
                'xg': stats.get('expected_goals', 0) if stats else 0,
                'posesion_promedio': stats.get('possession', 0) if stats else 0,
                'tiros_puerta': stats.get('shots_on_target', 0) if stats else 0,
                'efectividad': stats.get('conversion_rate', 0) if stats else 0
            }
        
        return {
            'equipo_local': procesar_estadisticas(pos_local, stats_local),
            'equipo_visitante': procesar_estadisticas(pos_visitante, stats_visitante)
        }
    
    def _obtener_datos_jugadores(self, equipo_local_id: int, equipo_visitante_id: int) -> Dict:
        """Obtiene datos individuales de jugadores"""
        jugadores_local = besoccer_service.obtener_jugadores_equipo(equipo_local_id)
        jugadores_visitante = besoccer_service.obtener_jugadores_equipo(equipo_visitante_id)
        
        def obtener_destacados(jugadores):
            goleador = max(jugadores, key=lambda j: j.get('goals', 0)) if jugadores else None
            asistente = max(jugadores, key=lambda j: j.get('assists', 0)) if jugadores else None
            portero = next((j for j in jugadores if j.get('position') == 'GK'), None) if jugadores else None
            
            return {
                'goleador': {
                    'nombre': goleador.get('name', '') if goleador else 'N/A',
                    'goles': goleador.get('goals', 0) if goleador else 0
                } if goleador else None,
                'asistente': {
                    'nombre': asistente.get('name', '') if asistente else 'N/A',
                    'asistencias': asistente.get('assists', 0) if asistente else 0
                } if asistente else None,
                'portero': {
                    'nombre': portero.get('name', '') if portero else 'N/A',
                    'atajadas_porcentaje': portero.get('save_percentage', 0) if portero else 0
                } if portero else None,
                'lesionados': [j for j in jugadores if j.get('injured', False)] if jugadores else [],
                'sancionados': [j for j in jugadores if j.get('suspended', False)] if jugadores else []
            }
        
        return {
            'equipo_local': obtener_destacados(jugadores_local),
            'equipo_visitante': obtener_destacados(jugadores_visitante)
        }

