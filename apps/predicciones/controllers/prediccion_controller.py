"""
Controlador para manejar la lógica de negocio de predicciones
"""
from typing import Dict, Optional
from django.contrib.auth import get_user_model
from apps.predicciones.models import Prediccion
from apps.predicciones.services import GeminiService
from apps.partidos.models import Partido
from apps.partidos.services import BesoccerService
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
Usuario = get_user_model()


class PrediccionController:
    """Controlador para gestionar predicciones"""
    
    def __init__(self):
        self.gemini_service = GeminiService()
        self.besoccer_service = BesoccerService()
    
    def crear_prediccion_ia(self, usuario, partido: Partido) -> Optional[Prediccion]:
        """Crea una predicción usando IA para un partido con datos detallados de Besoccer"""
        try:
            # Preparar datos básicos del partido
            partido_data = {
                'equipo_local': {
                    'nombre': partido.equipo_local.nombre,
                    'id': partido.equipo_local.id_api
                },
                'equipo_visitante': {
                    'nombre': partido.equipo_visitante.nombre,
                    'id': partido.equipo_visitante.id_api
                },
                'liga': {
                    'nombre': partido.liga.nombre,
                    'id': partido.liga.id_api
                },
                'fecha': partido.fecha.isoformat() if partido.fecha else datetime.now().isoformat()
            }
            
            # Obtener estadísticas detalladas de ambos equipos
            try:
                estadisticas_local = self._obtener_estadisticas_equipo(
                    partido.equipo_local.id_api,
                    partido.liga.id_api
                )
                if estadisticas_local:
                    partido_data['estadisticas_local'] = estadisticas_local
            except Exception as e:
                logger.warning(f"Error obteniendo estadísticas del equipo local: {e}")
            
            try:
                estadisticas_visitante = self._obtener_estadisticas_equipo(
                    partido.equipo_visitante.id_api,
                    partido.liga.id_api
                )
                if estadisticas_visitante:
                    partido_data['estadisticas_visitante'] = estadisticas_visitante
            except Exception as e:
                logger.warning(f"Error obteniendo estadísticas del equipo visitante: {e}")
            
            # Obtener últimos partidos de ambos equipos
            try:
                ultimos_partidos_local = self._obtener_ultimos_partidos_formateados(
                    partido.equipo_local.id_api
                )
                if ultimos_partidos_local:
                    partido_data['ultimos_partidos_local'] = ultimos_partidos_local
            except Exception as e:
                logger.warning(f"Error obteniendo últimos partidos del equipo local: {e}")
            
            try:
                ultimos_partidos_visitante = self._obtener_ultimos_partidos_formateados(
                    partido.equipo_visitante.id_api
                )
                if ultimos_partidos_visitante:
                    partido_data['ultimos_partidos_visitante'] = ultimos_partidos_visitante
            except Exception as e:
                logger.warning(f"Error obteniendo últimos partidos del equipo visitante: {e}")
            
            # Obtener historial de enfrentamientos (opcional)
            try:
                historial = self._obtener_historial_enfrentamientos(
                    partido.equipo_local.id_api,
                    partido.equipo_visitante.id_api
                )
                if historial:
                    partido_data['historial_enfrentamientos'] = historial
            except Exception as e:
                logger.warning(f"Error obteniendo historial de enfrentamientos: {e}")
            
            # Obtener predicción de Gemini con todos los datos
            prediccion_data = self.gemini_service.generar_prediccion(partido_data)
            
            # Crear o actualizar predicción
            prediccion, created = Prediccion.objects.update_or_create(
                usuario=usuario,
                partido=partido,
                defaults={
                    'goles_local_predicho': prediccion_data['goles_local'],
                    'goles_visitante_predicho': prediccion_data['goles_visitante'],
                    'prediccion_ia': prediccion_data['analisis'],
                    'confianza': prediccion_data['confianza']
                }
            )
            
            return prediccion
            
        except Exception as e:
            logger.error(f"Error al crear predicción: {e}", exc_info=True)
            return None
    
    def _obtener_estadisticas_equipo(self, equipo_id: int, liga_id: int) -> Optional[Dict]:
        """Obtiene y formatea las estadísticas de un equipo"""
        try:
            # Obtener estadísticas de la API
            stats = self.besoccer_service.obtener_estadisticas_equipo_detalladas(equipo_id)
            if not stats:
                return None
            
            # Formatear estadísticas
            estadisticas = {}
            
            # Estadísticas generales
            if 'played' in stats:
                estadisticas['partidos_jugados'] = stats['played']
            if 'wins' in stats:
                estadisticas['victorias'] = stats['wins']
            if 'draws' in stats:
                estadisticas['empates'] = stats['draws']
            if 'losses' in stats:
                estadisticas['derrotas'] = stats['losses']
            if 'points' in stats:
                estadisticas['puntos'] = stats['points']
            if 'position' in stats:
                estadisticas['posicion'] = stats['position']
            
            # Goles
            if 'goals_for' in stats or 'gf' in stats:
                estadisticas['goles_a_favor'] = stats.get('goals_for') or stats.get('gf', 0)
            if 'goals_against' in stats or 'ga' in stats:
                estadisticas['goles_en_contra'] = stats.get('goals_against') or stats.get('ga', 0)
            if 'goal_difference' in stats or 'gd' in stats:
                estadisticas['diferencia_goles'] = stats.get('goal_difference') or stats.get('gd', 0)
            
            # Calcular promedios
            if estadisticas.get('partidos_jugados', 0) > 0:
                estadisticas['promedio_goles_favor'] = estadisticas.get('goles_a_favor', 0) / estadisticas['partidos_jugados']
                estadisticas['promedio_goles_contra'] = estadisticas.get('goles_en_contra', 0) / estadisticas['partidos_jugados']
            
            # Estadísticas de local/visitante si están disponibles
            if 'home' in stats:
                estadisticas['estadisticas_local'] = {
                    'victorias': stats['home'].get('wins', 0),
                    'empates': stats['home'].get('draws', 0),
                    'derrotas': stats['home'].get('losses', 0),
                    'goles_favor': stats['home'].get('goals_for', 0),
                    'goles_contra': stats['home'].get('goals_against', 0)
                }
            
            if 'away' in stats:
                estadisticas['estadisticas_visitante'] = {
                    'victorias': stats['away'].get('wins', 0),
                    'empates': stats['away'].get('draws', 0),
                    'derrotas': stats['away'].get('losses', 0),
                    'goles_favor': stats['away'].get('goals_for', 0),
                    'goles_contra': stats['away'].get('goals_against', 0)
                }
            
            return estadisticas if estadisticas else None
            
        except Exception as e:
            logger.warning(f"Error formateando estadísticas del equipo {equipo_id}: {e}")
            return None
    
    def _obtener_ultimos_partidos_formateados(self, equipo_id: int, limite: int = 5) -> list:
        """Obtiene y formatea los últimos partidos de un equipo"""
        try:
            partidos = self.besoccer_service.obtener_ultimos_partidos_equipo(equipo_id, limite)
            if not partidos:
                return []
            
            partidos_formateados = []
            for partido in partidos:
                # Determinar si el equipo jugó como local o visitante
                home_team_id = partido.get('home_team', {}).get('id') if isinstance(partido.get('home_team'), dict) else None
                away_team_id = partido.get('away_team', {}).get('id') if isinstance(partido.get('away_team'), dict) else None
                
                condicion = 'local' if home_team_id == equipo_id else 'visitante'
                
                # Obtener nombres de equipos
                if condicion == 'local':
                    rival_nombre = partido.get('away_team', {}).get('name', 'Rival') if isinstance(partido.get('away_team'), dict) else 'Rival'
                    goles_equipo = partido.get('home_score', 0)
                    goles_rival = partido.get('away_score', 0)
                else:
                    rival_nombre = partido.get('home_team', {}).get('name', 'Rival') if isinstance(partido.get('home_team'), dict) else 'Rival'
                    goles_equipo = partido.get('away_score', 0)
                    goles_rival = partido.get('home_score', 0)
                
                # Formatear resultado
                resultado = f"{goles_equipo}-{goles_rival}"
                
                # Fecha
                fecha = partido.get('date', '') or partido.get('datetime', '')
                
                partidos_formateados.append({
                    'resultado': resultado,
                    'rival': rival_nombre,
                    'fecha': fecha,
                    'condicion': condicion
                })
            
            return partidos_formateados
            
        except Exception as e:
            logger.warning(f"Error formateando últimos partidos del equipo {equipo_id}: {e}")
            return []
    
    def _obtener_historial_enfrentamientos(self, equipo_local_id: int, equipo_visitante_id: int) -> list:
        """Obtiene el historial de enfrentamientos entre dos equipos"""
        try:
            # Obtener últimos partidos del equipo local y filtrar los que fueron contra el visitante
            partidos_local = self.besoccer_service.obtener_ultimos_partidos_equipo(equipo_local_id, 20)
            
            historial = []
            for partido in partidos_local:
                home_id = partido.get('home_team', {}).get('id') if isinstance(partido.get('home_team'), dict) else None
                away_id = partido.get('away_team', {}).get('id') if isinstance(partido.get('away_team'), dict) else None
                
                # Verificar si este partido fue contra el equipo visitante
                if (home_id == equipo_local_id and away_id == equipo_visitante_id) or \
                   (home_id == equipo_visitante_id and away_id == equipo_local_id):
                    resultado = f"{partido.get('home_score', 0)}-{partido.get('away_score', 0)}"
                    fecha = partido.get('date', '') or partido.get('datetime', '')
                    historial.append({
                        'resultado': resultado,
                        'fecha': fecha
                    })
            
            return historial[:5]  # Últimos 5 enfrentamientos
            
        except Exception as e:
            logger.warning(f"Error obteniendo historial de enfrentamientos: {e}")
            return []
    
    def crear_prediccion_manual(self, usuario, partido: Partido, goles_local: int, goles_visitante: int) -> Prediccion:
        """Crea una predicción manual del usuario"""
        prediccion, created = Prediccion.objects.update_or_create(
            usuario=usuario,
            partido=partido,
            defaults={
                'goles_local_predicho': goles_local,
                'goles_visitante_predicho': goles_visitante,
                'confianza': 0.0  # Predicción manual sin confianza de IA
            }
        )
        return prediccion
    
    def obtener_predicciones_usuario(self, usuario, limite: int = 10):
        """Obtiene las predicciones de un usuario"""
        return Prediccion.objects.filter(
            usuario=usuario
        ).select_related('partido', 'partido__equipo_local', 'partido__equipo_visitante', 'partido__liga').order_by('-fecha_prediccion')[:limite]
    
    def verificar_predicciones_pendientes(self):
        """Verifica todas las predicciones de partidos finalizados"""
        predicciones = Prediccion.objects.filter(
            es_correcta__isnull=True,
            partido__estado='FT'
        )
        
        for prediccion in predicciones:
            prediccion.verificar_prediccion()
        
        return predicciones.count()
    
    def obtener_estadisticas_usuario(self, usuario) -> Dict:
        """Obtiene estadísticas de predicciones del usuario"""
        total = Prediccion.objects.filter(usuario=usuario).count()
        correctas = Prediccion.objects.filter(usuario=usuario, es_correcta=True).count()
        incorrectas = Prediccion.objects.filter(usuario=usuario, es_correcta=False).count()
        pendientes = Prediccion.objects.filter(usuario=usuario, es_correcta__isnull=True).count()
        
        precision = (correctas / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'correctas': correctas,
            'incorrectas': incorrectas,
            'pendientes': pendientes,
            'precision': round(precision, 2)
        }

