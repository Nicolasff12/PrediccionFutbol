"""
Servicio para interactuar con la API de Besoccer
Estructura correcta: usa 'method' en lugar de 'req', y 'competition' en lugar de 'league'
"""
import requests
import json
from django.conf import settings
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class BesoccerService:
    """Clase para manejar las peticiones a la API de Besoccer"""
    
    BASE_URL = "https://apiclient.besoccerapps.com/scripts/api/api.php"
    DEFAULT_COMPETITION = "colombia_primera_a"  # Liga BetPlay Colombia
    DEFAULT_LEAGUE_ID = 50  # ID de la Liga BetPlay Colombia en BeSoccer
    
    def __init__(self):
        self.api_key = settings.BESOCCER_API_KEY
        self.token = getattr(settings, 'BESOCCER_TOKEN', None)
    
    def _make_request(self, method: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Realiza una petición a la API de BeSoccer
        
        Args:
            method: Método de la API (ej: 'matches.next', 'standings', 'team.stats')
            params: Parámetros adicionales para la petición
        """
        try:
            # Parámetros base
            request_params = {
                'key': self.api_key,
                'format': 'json',
                'method': method
            }
            
            # Agregar token si está disponible
            if self.token:
                request_params['token'] = self.token
            
            # Agregar parámetros adicionales
            if params:
                request_params.update(params)
            
            response = requests.get(self.BASE_URL, params=request_params, timeout=10)
            response.raise_for_status()
            
            # Intentar parsear JSON
            try:
                data = response.json()
                return data
            except json.JSONDecodeError:
                # Si no es JSON, puede ser un mensaje de error
                error_text = response.text
                if 'not-allowed-request-for-api-account-type' in error_text:
                    logger.warning(f"Method '{method}' no permitido para este tipo de cuenta API")
                    return None
                logger.error(f"Error parseando JSON: {error_text[:200]}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición a Besoccer: {e}")
            return None
    
    def obtener_equipos_liga(self, competition_id: str = None, league_id: int = None) -> List[Dict]:
        """Obtiene los equipos de una liga/competition"""
        # Usar league_id si se proporciona, sino usar el default de Colombia (50)
        if league_id is None:
            league_id = self.DEFAULT_LEAGUE_ID  # Liga BetPlay Colombia (50)
        
        # Intentar primero con el método antiguo que sabemos que funciona (req=teams)
        # Este método usa la estructura antigua pero funciona con el plan actual
        try:
            request_params = {
                'key': self.api_key,
                'format': 'json',
                'req': 'teams',
                'league': league_id  # Liga Colombia (50) por defecto
            }
            if self.token:
                request_params['token'] = self.token
            
            response = requests.get(self.BASE_URL, params=request_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and 'team' in data:
                return data['team'] if isinstance(data['team'], list) else [data['team']]
        except Exception as e:
            logger.warning(f"Error obteniendo equipos con método antiguo: {e}")
        
        # Si falla, intentar con el método nuevo
        params = {'league': league_id}
        data = self._make_request('teams', params)
        if data and 'team' in data:
            return data['team'] if isinstance(data['team'], list) else [data['team']]
        return []
    
    def obtener_partidos_proximos(self, competition_id: str = None, limite: int = 10) -> List[Dict]:
        """Obtiene los próximos partidos de una liga"""
        params = {
            'limit': limite
        }
        if competition_id:
            params['competition'] = competition_id
        else:
            params['competition'] = self.DEFAULT_COMPETITION
        
        data = self._make_request('matches.next', params)
        if data:
            # La estructura de respuesta puede variar
            if 'match' in data:
                return data['match'] if isinstance(data['match'], list) else [data['match']]
            elif 'matches' in data:
                return data['matches'] if isinstance(data['matches'], list) else [data['matches']]
            elif isinstance(data, list):
                return data
        return []
    
    def obtener_partidos_coming(self, competition_id: int = None, limite: int = 10) -> List[Dict]:
        """Obtiene los próximos partidos (alias para compatibilidad)"""
        comp_id = None
        if competition_id:
            comp_id = str(competition_id)
        return self.obtener_partidos_proximos(comp_id, limite)
    
    def obtener_tabla_posiciones(self, competition_id: str = None) -> List[Dict]:
        """Obtiene la tabla de posiciones (standings)"""
        params = {}
        if competition_id:
            params['competition'] = competition_id
        else:
            params['competition'] = self.DEFAULT_COMPETITION
        
        data = self._make_request('standings', params)
        if data:
            # La estructura puede variar
            if 'table' in data:
                return data['table'] if isinstance(data['table'], list) else [data['table']]
            elif 'standings' in data:
                return data['standings'] if isinstance(data['standings'], list) else [data['standings']]
            elif 'team' in data:
                return data['team'] if isinstance(data['team'], list) else [data['team']]
            elif isinstance(data, list):
                return data
        return []
    
    def obtener_ultimos_partidos_equipo(self, equipo_id: int, limite: int = 5) -> List[Dict]:
        """Obtiene los últimos partidos de un equipo"""
        params = {
            'team': equipo_id,
            'limit': limite
        }
        
        data = self._make_request('matches.team', params)
        if data:
            if 'match' in data:
                matches = data['match'] if isinstance(data['match'], list) else [data['match']]
                # Filtrar partidos finalizados y ordenar por fecha descendente
                finished = [m for m in matches if m.get('status') == 'FT' or m.get('finished', False)]
                finished.sort(key=lambda x: x.get('date', ''), reverse=True)
                return finished[:limite]
            elif isinstance(data, list):
                return data[:limite]
        return []
    
    def obtener_estadisticas_equipo_detalladas(self, equipo_id: int, competition_id: str = None) -> Optional[Dict]:
        """Obtiene estadísticas detalladas de un equipo"""
        params = {
            'team': equipo_id
        }
        if competition_id:
            params['competition'] = competition_id
        
        data = self._make_request('team.stats', params)
        return data
    
    def obtener_estadisticas_equipo(self, equipo_id: int, competition_id: str = None) -> Optional[Dict]:
        """Obtiene estadísticas de un equipo (alias)"""
        return self.obtener_estadisticas_equipo_detalladas(equipo_id, competition_id)
    
    def obtener_partidos_equipo_local(self, equipo_id: int, limite: int = 5) -> List[Dict]:
        """Obtiene los últimos partidos como local de un equipo"""
        # Usar matches.team y filtrar por venue después
        partidos = self.obtener_ultimos_partidos_equipo(equipo_id, limite * 2)
        return [p for p in partidos if p.get('venue') == 'home' or p.get('home_team', {}).get('id') == equipo_id][:limite]
    
    def obtener_partidos_equipo_visitante(self, equipo_id: int, limite: int = 5) -> List[Dict]:
        """Obtiene los últimos partidos como visitante de un equipo"""
        # Usar matches.team y filtrar por venue después
        partidos = self.obtener_ultimos_partidos_equipo(equipo_id, limite * 2)
        return [p for p in partidos if p.get('venue') == 'away' or p.get('away_team', {}).get('id') == equipo_id][:limite]
    
    def obtener_detalle_partido(self, partido_id: int) -> Optional[Dict]:
        """Obtiene el detalle de un partido específico"""
        data = self._make_request('match', {'id': partido_id})
        if data and 'match' in data:
            return data['match'] if isinstance(data['match'], dict) else data['match'][0] if data['match'] else None
        return None
    
    def obtener_jugadores_equipo(self, equipo_id: int) -> List[Dict]:
        """Obtiene los jugadores de un equipo"""
        data = self._make_request('players', {'team': equipo_id})
        if data and 'player' in data:
            return data['player'] if isinstance(data['player'], list) else [data['player']]
        return []
    
    def obtener_goleadores_liga(self, competition_id: str = None, limite: int = 10) -> List[Dict]:
        """Obtiene los máximos goleadores de la liga"""
        params = {'limit': limite}
        if competition_id:
            params['competition'] = competition_id
        else:
            params['competition'] = self.DEFAULT_COMPETITION
        
        data = self._make_request('top_scorers', params)
        if data and 'player' in data:
            return data['player'] if isinstance(data['player'], list) else [data['player']]
        return []
    
    def obtener_estadisticas_liga(self, competition_id: str = None) -> Optional[Dict]:
        """Obtiene estadísticas globales de la liga"""
        params = {}
        if competition_id:
            params['competition'] = competition_id
        else:
            params['competition'] = self.DEFAULT_COMPETITION
        
        data = self._make_request('league_stats', params)
        return data
    
    # Métodos de compatibilidad con código existente
    def obtener_ligas(self, pais: str = "Colombia") -> List[Dict]:
        """Obtiene las ligas disponibles (compatibilidad)"""
        # Este método puede no estar disponible con el plan actual
        return []
    
    def obtener_liga_betplay(self) -> Optional[Dict]:
        """Obtiene información de la Liga BetPlay (compatibilidad)"""
        return {'id': self.DEFAULT_LEAGUE_ID, 'name': 'Liga BetPlay Dimayor', 'competition': self.DEFAULT_COMPETITION, 'pais': 'Colombia'}
    
    def obtener_partidos_liga(self, liga_id: int, fecha_inicio: str = None, fecha_fin: str = None) -> List[Dict]:
        """Obtiene los partidos de una liga específica (compatibilidad)"""
        return self.obtener_partidos_proximos(self.DEFAULT_COMPETITION, 20)
    
    def obtener_partidos_live(self) -> List[Dict]:
        """Obtiene partidos en vivo"""
        data = self._make_request('matches.live', {})
        if data:
            if 'match' in data:
                return data['match'] if isinstance(data['match'], list) else [data['match']]
            elif isinstance(data, list):
                return data
        return []
