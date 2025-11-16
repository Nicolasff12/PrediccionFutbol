"""
Servicio para interactuar con la API de Google Gemini
"""
import google.generativeai as genai
from django.conf import settings
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class GeminiService:
    """Clase para manejar las predicciones con Gemini AI"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY no configurada")
    
    def generar_prediccion(self, partido_data: Dict) -> Dict:
        """
        Genera una predicción para un partido usando Gemini AI
        
        Args:
            partido_data: Diccionario con información del partido
        
        Returns:
            Dict con predicción, análisis y confianza
        """
        if not self.model:
            return {
                'goles_local': 1,
                'goles_visitante': 1,
                'analisis': 'API de Gemini no configurada',
                'confianza': 50.0
            }
        
        try:
            # Construir el prompt para Gemini
            prompt = self._construir_prompt(partido_data)
            
            # Generar respuesta
            response = self.model.generate_content(prompt)
            
            # Procesar respuesta
            return self._procesar_respuesta(response.text, partido_data)
            
        except Exception as e:
            logger.error(f"Error al generar predicción con Gemini: {e}")
            return {
                'goles_local': 1,
                'goles_visitante': 1,
                'analisis': f'Error al generar predicción: {str(e)}',
                'confianza': 50.0
            }
    
    def _construir_prompt(self, partido_data: Dict) -> str:
        """Construye el prompt para Gemini"""
        equipo_local = partido_data.get('equipo_local', {}).get('nombre', 'Equipo Local')
        equipo_visitante = partido_data.get('equipo_visitante', {}).get('nombre', 'Equipo Visitante')
        fecha = partido_data.get('fecha', '')
        liga = partido_data.get('liga', {}).get('nombre', 'Liga')
        
        # Estadísticas si están disponibles
        estadisticas_local = partido_data.get('estadisticas_local', {})
        estadisticas_visitante = partido_data.get('estadisticas_visitante', {})
        
        prompt = f"""
Eres un experto analista de fútbol. Analiza el siguiente partido y proporciona una predicción detallada.

PARTIDO:
- Liga: {liga}
- Equipo Local: {equipo_local}
- Equipo Visitante: {equipo_visitante}
- Fecha: {fecha}

"""
        
        if estadisticas_local or estadisticas_visitante:
            prompt += "ESTADÍSTICAS:\n"
            if estadisticas_local:
                prompt += f"- {equipo_local}: {estadisticas_local}\n"
            if estadisticas_visitante:
                prompt += f"- {equipo_visitante}: {estadisticas_visitante}\n"
        
        prompt += """
Por favor, proporciona:
1. Predicción del marcador final (formato: X-Y donde X son goles del local e Y del visitante)
2. Un análisis breve (2-3 párrafos) explicando tu predicción
3. Nivel de confianza (0-100)

Responde en formato JSON:
{
    "goles_local": X,
    "goles_visitante": Y,
    "analisis": "tu análisis aquí",
    "confianza": Z
}
"""
        
        return prompt
    
    def _procesar_respuesta(self, respuesta: str, partido_data: Dict) -> Dict:
        """Procesa la respuesta de Gemini y extrae la información"""
        import json
        import re
        
        try:
            # Intentar extraer JSON de la respuesta
            json_match = re.search(r'\{[^}]+\}', respuesta, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return {
                    'goles_local': int(data.get('goles_local', 1)),
                    'goles_visitante': int(data.get('goles_visitante', 1)),
                    'analisis': data.get('analisis', respuesta),
                    'confianza': float(data.get('confianza', 50.0))
                }
        except:
            pass
        
        # Si no se puede parsear JSON, intentar extraer números del texto
        numeros = re.findall(r'\d+', respuesta)
        goles_local = int(numeros[0]) if len(numeros) > 0 else 1
        goles_visitante = int(numeros[1]) if len(numeros) > 1 else 1
        
        return {
            'goles_local': goles_local,
            'goles_visitante': goles_visitante,
            'analisis': respuesta,
            'confianza': 50.0
        }

