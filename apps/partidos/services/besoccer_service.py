"""
Servicio para interactuar con la API de Besoccer
"""
import requests
from django.conf import settings
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class BesoccerService:
    """Clase para manejar las peticiones a la API de Besoccer"""
    
    BASE_URL = "https://api.besoccer.com"
    
    def __init__(self):
        self.api_key = settings.BESOCCER_API_KEY
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Realiza una petición a la API"""
        try:
            url = f"{self.BASE_URL}{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición a Besoccer: {e}")
            return None
    
    def obtener_ligas(self, pais: str = "Colombia") -> List[Dict]:
        """Obtiene las ligas disponibles"""
        endpoint = "/leagues"
        params = {'country': pais}
        data = self._make_request(endpoint, params)
        if data and 'data' in data:
            return data['data']
        return []
    
    def obtener_liga_betplay(self) -> Optional[Dict]:
        """Obtiene información de la Liga BetPlay"""
        ligas = self.obtener_ligas("Colombia")
        for liga in ligas:
            if 'betplay' in liga.get('name', '').lower() or liga.get('id') == 1:
                return liga
        return None
    
    def obtener_partidos_liga(self, liga_id: int, fecha_inicio: str = None, fecha_fin: str = None) -> List[Dict]:
        """Obtiene los partidos de una liga específica"""
        endpoint = f"/matches/league/{liga_id}"
        params = {}
        if fecha_inicio:
            params['date_from'] = fecha_inicio
        if fecha_fin:
            params['date_to'] = fecha_fin
        data = self._make_request(endpoint, params)
        if data and 'data' in data:
            return data['data']
        return []
    
    def obtener_partidos_proximos(self, liga_id: int, dias: int = 7) -> List[Dict]:
        """Obtiene los próximos partidos de una liga"""
        from datetime import datetime, timedelta
        fecha_inicio = datetime.now().strftime('%Y-%m-%d')
        fecha_fin = (datetime.now() + timedelta(days=dias)).strftime('%Y-%m-%d')
        return self.obtener_partidos_liga(liga_id, fecha_inicio, fecha_fin)
    
    def obtener_equipos_liga(self, liga_id: int) -> List[Dict]:
        """Obtiene los equipos de una liga"""
        endpoint = f"/teams/league/{liga_id}"
        data = self._make_request(endpoint)
        if data and 'data' in data:
            return data['data']
        return []
    
    def obtener_detalle_partido(self, partido_id: int) -> Optional[Dict]:
        """Obtiene el detalle de un partido específico"""
        endpoint = f"/matches/{partido_id}"
        return self._make_request(endpoint)
    
    def obtener_estadisticas_equipo(self, equipo_id: int) -> Optional[Dict]:
        """Obtiene estadísticas de un equipo"""
        endpoint = f"/teams/{equipo_id}/stats"
        return self._make_request(endpoint)

