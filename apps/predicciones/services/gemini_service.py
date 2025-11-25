"""
Servicio para interactuar con la API de Google Gemini
"""
import google.generativeai as genai
from django.conf import settings
from typing import Dict, Optional, List
import logging
import json
import re

logger = logging.getLogger(__name__)


class GeminiService:
    """Clase para manejar las predicciones con Gemini AI"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = None
        self.model_name = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # Listar modelos disponibles y seleccionar uno compatible
                self.model, self.model_name = self._seleccionar_modelo_compatible()
                
                if self.model:
                    logger.info(f"Modelo Gemini seleccionado: {self.model_name}")
                else:
                    logger.warning("No se pudo encontrar un modelo compatible de Gemini")
            except Exception as e:
                logger.error(f"Error configurando Gemini: {e}", exc_info=True)
                self.model = None
        else:
            logger.warning("GEMINI_API_KEY no configurada")
    
    def _seleccionar_modelo_compatible(self):
        """
        Selecciona un modelo compatible de Gemini.
        Intenta con diferentes modelos en orden de preferencia.
        """
        # Lista de modelos a intentar en orden de preferencia (modelos actuales disponibles)
        modelos_a_intentar = [
            'gemini-2.0-flash',  # Modelo rápido y eficiente
            'models/gemini-2.0-flash',  # Con prefijo models/
            'gemini-2.5-flash',  # Versión más reciente
            'models/gemini-2.5-flash',  # Con prefijo models/
            'gemini-2.0-flash-001',  # Versión específica
            'models/gemini-2.0-flash-001',  # Con prefijo models/
            'gemini-2.5-pro',  # Modelo pro
            'models/gemini-2.5-pro',  # Con prefijo models/
        ]
        
        for modelo_nombre in modelos_a_intentar:
            try:
                model = genai.GenerativeModel(modelo_nombre)
                # Hacer una prueba rápida para verificar que funciona
                # (no generamos contenido, solo verificamos que el modelo existe)
                logger.info(f"Modelo {modelo_nombre} encontrado y disponible")
                return model, modelo_nombre
            except Exception as e:
                logger.debug(f"Modelo {modelo_nombre} no disponible: {e}")
                continue
        
        # Si ningún modelo funciona, intentar listar modelos disponibles
        try:
            modelos_disponibles = genai.list_models()
            for modelo in modelos_disponibles:
                # Buscar modelos que soporten generateContent y contengan "gemini" y "flash"
                if ('generateContent' in modelo.supported_generation_methods and 
                    'gemini' in modelo.name.lower() and 
                    'flash' in modelo.name.lower()):
                    try:
                        model = genai.GenerativeModel(modelo.name)
                        logger.info(f"Usando modelo disponible encontrado: {modelo.name}")
                        return model, modelo.name
                    except:
                        continue
        except Exception as e:
            logger.warning(f"No se pudieron listar modelos disponibles: {e}")
        
        return None, None
    
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
            
            # Configurar parámetros de generación (algunos modelos pueden no soportar todos)
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
            
            # Generar respuesta
            # Intentar con generation_config primero, si falla intentar sin él
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
            except Exception as config_error:
                logger.warning(f"Error con generation_config, intentando sin configuración: {config_error}")
                # Intentar sin generation_config (algunas versiones no lo soportan)
                response = self.model.generate_content(prompt)
            
            # Obtener el texto de la respuesta
            if hasattr(response, 'text'):
                respuesta_texto = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                respuesta_texto = response.candidates[0].content.parts[0].text
            else:
                respuesta_texto = str(response)
            
            # Procesar respuesta
            return self._procesar_respuesta(respuesta_texto, partido_data)
            
        except Exception as e:
            logger.error(f"Error al generar predicción con Gemini: {e}", exc_info=True)
            # Si el error es por modelo no encontrado, intentar reconfigurar
            if "not found" in str(e).lower() or "not supported" in str(e).lower():
                logger.info("Intentando reconfigurar modelo...")
                self.model, self.model_name = self._seleccionar_modelo_compatible()
                if self.model:
                    logger.info(f"Modelo reconfigurado a: {self.model_name}")
                    # Intentar de nuevo una vez
                    try:
                        prompt = self._construir_prompt(partido_data)
                        response = self.model.generate_content(prompt)
                        if hasattr(response, 'text'):
                            respuesta_texto = response.text
                        else:
                            respuesta_texto = str(response)
                        return self._procesar_respuesta(respuesta_texto, partido_data)
                    except:
                        pass
            
            return {
                'goles_local': 1,
                'goles_visitante': 1,
                'analisis': f'Error al generar predicción: {str(e)}',
                'confianza': 50.0
            }
    
    def _construir_prompt(self, partido_data: Dict) -> str:
        """Construye el prompt para Gemini con información detallada"""
        equipo_local = partido_data.get('equipo_local', {})
        equipo_visitante = partido_data.get('equipo_visitante', {})
        liga = partido_data.get('liga', {})
        fecha = partido_data.get('fecha', '')
        
        nombre_local = equipo_local.get('nombre', 'Equipo Local')
        nombre_visitante = equipo_visitante.get('nombre', 'Equipo Visitante')
        nombre_liga = liga.get('nombre', 'Liga')
        
        # Construir el prompt base
        prompt = f"""Eres un experto analista de fútbol profesional con años de experiencia en análisis de partidos y predicciones. 
Analiza el siguiente partido y proporciona una predicción detallada y fundamentada.

═══════════════════════════════════════════════════════════════
INFORMACIÓN DEL PARTIDO
═══════════════════════════════════════════════════════════════
Liga: {nombre_liga}
Equipo Local: {nombre_local}
Equipo Visitante: {nombre_visitante}
Fecha: {fecha}

"""
        
        # Agregar estadísticas del equipo local
        estadisticas_local = partido_data.get('estadisticas_local', {})
        if estadisticas_local:
            prompt += f"═══════════════════════════════════════════════════════════════\n"
            prompt += f"ESTADÍSTICAS DE {nombre_local.upper()}\n"
            prompt += f"═══════════════════════════════════════════════════════════════\n"
            prompt += self._formatear_estadisticas(estadisticas_local)
            prompt += "\n"
        
        # Agregar estadísticas del equipo visitante
        estadisticas_visitante = partido_data.get('estadisticas_visitante', {})
        if estadisticas_visitante:
            prompt += f"═══════════════════════════════════════════════════════════════\n"
            prompt += f"ESTADÍSTICAS DE {nombre_visitante.upper()}\n"
            prompt += f"═══════════════════════════════════════════════════════════════\n"
            prompt += self._formatear_estadisticas(estadisticas_visitante)
            prompt += "\n"
        
        # Agregar últimos partidos del equipo local
        ultimos_partidos_local = partido_data.get('ultimos_partidos_local', [])
        if ultimos_partidos_local:
            prompt += f"═══════════════════════════════════════════════════════════════\n"
            prompt += f"ÚLTIMOS PARTIDOS DE {nombre_local.upper()}\n"
            prompt += f"═══════════════════════════════════════════════════════════════\n"
            prompt += self._formatear_ultimos_partidos(ultimos_partidos_local, nombre_local)
            prompt += "\n"
        
        # Agregar últimos partidos del equipo visitante
        ultimos_partidos_visitante = partido_data.get('ultimos_partidos_visitante', [])
        if ultimos_partidos_visitante:
            prompt += f"═══════════════════════════════════════════════════════════════\n"
            prompt += f"ÚLTIMOS PARTIDOS DE {nombre_visitante.upper()}\n"
            prompt += f"═══════════════════════════════════════════════════════════════\n"
            prompt += self._formatear_ultimos_partidos(ultimos_partidos_visitante, nombre_visitante)
            prompt += "\n"
        
        # Agregar historial entre equipos si está disponible
        historial = partido_data.get('historial_enfrentamientos', [])
        if historial:
            prompt += f"═══════════════════════════════════════════════════════════════\n"
            prompt += f"HISTORIAL DE ENFRENTAMIENTOS\n"
            prompt += f"═══════════════════════════════════════════════════════════════\n"
            prompt += self._formatear_historial(historial, nombre_local, nombre_visitante)
            prompt += "\n"
        
        # Agregar tabla de posiciones si está disponible
        tabla_posiciones = partido_data.get('tabla_posiciones', [])
        if tabla_posiciones:
            prompt += f"═══════════════════════════════════════════════════════════════\n"
            prompt += f"TABLA DE POSICIONES (Top 10)\n"
            prompt += f"═══════════════════════════════════════════════════════════════\n"
            prompt += self._formatear_tabla_posiciones(tabla_posiciones)
            prompt += "\n"
        
        # Instrucciones finales
        prompt += """═══════════════════════════════════════════════════════════════
INSTRUCCIONES
═══════════════════════════════════════════════════════════════

Basándote en toda la información proporcionada, analiza:
1. La forma reciente de ambos equipos (últimos partidos)
2. Las estadísticas ofensivas y defensivas de cada equipo
3. La posición en la tabla de posiciones (si está disponible)
4. El historial de enfrentamientos entre ambos equipos (si está disponible)
5. La ventaja de jugar en casa para el equipo local
6. Las estadísticas como local vs visitante
7. Cualquier factor relevante que pueda influir en el resultado

Proporciona:
1. Una predicción del marcador final (goles del local y del visitante)
2. Un análisis detallado (3-4 párrafos) explicando tu predicción, considerando:
   - Fortalezas y debilidades de cada equipo
   - Factores tácticos y de forma
   - Contexto del partido
3. Un nivel de confianza (0-100) basado en la solidez de tu análisis

IMPORTANTE: Responde ÚNICAMENTE en formato JSON válido, sin texto adicional antes o después:

{
    "goles_local": <número entero>,
    "goles_visitante": <número entero>,
    "analisis": "<análisis detallado en español, 3-4 párrafos>",
    "confianza": <número entre 0 y 100>
}

Ejemplo de respuesta esperada:
{
    "goles_local": 2,
    "goles_visitante": 1,
    "analisis": "El equipo local muestra una forma sólida en casa con 4 victorias en los últimos 5 partidos...",
    "confianza": 75.5
}
"""
        
        return prompt
    
    def _formatear_estadisticas(self, estadisticas: Dict) -> str:
        """Formatea las estadísticas de un equipo para el prompt"""
        texto = ""
        
        # Estadísticas generales
        if 'partidos_jugados' in estadisticas or 'played' in estadisticas:
            jugados = estadisticas.get('partidos_jugados') or estadisticas.get('played', 0)
            texto += f"Partidos jugados: {jugados}\n"
        
        if 'victorias' in estadisticas or 'wins' in estadisticas:
            victorias = estadisticas.get('victorias') or estadisticas.get('wins', 0)
            texto += f"Victorias: {victorias}\n"
        
        if 'empates' in estadisticas or 'draws' in estadisticas:
            empates = estadisticas.get('empates') or estadisticas.get('draws', 0)
            texto += f"Empates: {empates}\n"
        
        if 'derrotas' in estadisticas or 'losses' in estadisticas:
            derrotas = estadisticas.get('derrotas') or estadisticas.get('losses', 0)
            texto += f"Derrotas: {derrotas}\n"
        
        if 'puntos' in estadisticas or 'points' in estadisticas:
            puntos = estadisticas.get('puntos') or estadisticas.get('points', 0)
            texto += f"Puntos: {puntos}\n"
        
        if 'posicion' in estadisticas or 'position' in estadisticas:
            posicion = estadisticas.get('posicion') or estadisticas.get('position', 0)
            texto += f"Posición en tabla: {posicion}\n"
        
        # Goles
        if 'goles_a_favor' in estadisticas or 'goals_for' in estadisticas or 'gf' in estadisticas:
            gf = estadisticas.get('goles_a_favor') or estadisticas.get('goals_for') or estadisticas.get('gf', 0)
            texto += f"Goles a favor: {gf}\n"
        
        if 'goles_en_contra' in estadisticas or 'goals_against' in estadisticas or 'ga' in estadisticas:
            gc = estadisticas.get('goles_en_contra') or estadisticas.get('goals_against') or estadisticas.get('ga', 0)
            texto += f"Goles en contra: {gc}\n"
        
        if 'diferencia_goles' in estadisticas or 'goal_difference' in estadisticas or 'gd' in estadisticas:
            dif = estadisticas.get('diferencia_goles') or estadisticas.get('goal_difference') or estadisticas.get('gd', 0)
            texto += f"Diferencia de goles: {dif}\n"
        
        # Promedios
        if 'promedio_goles_favor' in estadisticas:
            texto += f"Promedio goles a favor por partido: {estadisticas['promedio_goles_favor']:.2f}\n"
        
        if 'promedio_goles_contra' in estadisticas:
            texto += f"Promedio goles en contra por partido: {estadisticas['promedio_goles_contra']:.2f}\n"
        
        # Estadísticas de local/visitante
        if 'estadisticas_local' in estadisticas:
            local_stats = estadisticas['estadisticas_local']
            texto += f"\nComo local:\n"
            texto += f"  Victorias: {local_stats.get('victorias', 0)}\n"
            texto += f"  Empates: {local_stats.get('empates', 0)}\n"
            texto += f"  Derrotas: {local_stats.get('derrotas', 0)}\n"
            texto += f"  Goles a favor: {local_stats.get('goles_favor', 0)}\n"
            texto += f"  Goles en contra: {local_stats.get('goles_contra', 0)}\n"
        
        if 'estadisticas_visitante' in estadisticas:
            visitante_stats = estadisticas['estadisticas_visitante']
            texto += f"\nComo visitante:\n"
            texto += f"  Victorias: {visitante_stats.get('victorias', 0)}\n"
            texto += f"  Empates: {visitante_stats.get('empates', 0)}\n"
            texto += f"  Derrotas: {visitante_stats.get('derrotas', 0)}\n"
            texto += f"  Goles a favor: {visitante_stats.get('goles_favor', 0)}\n"
            texto += f"  Goles en contra: {visitante_stats.get('goles_contra', 0)}\n"
        
        return texto if texto else "Estadísticas no disponibles"
    
    def _formatear_ultimos_partidos(self, partidos: List[Dict], nombre_equipo: str) -> str:
        """Formatea los últimos partidos de un equipo"""
        if not partidos:
            return "No hay información de partidos recientes"
        
        texto = ""
        for i, partido in enumerate(partidos[:5], 1):  # Últimos 5 partidos
            resultado = partido.get('resultado', '')
            rival = partido.get('rival', '')
            fecha = partido.get('fecha', '')
            condicion = partido.get('condicion', '')  # 'local' o 'visitante'
            
            texto += f"{i}. {resultado} vs {rival} ({condicion})"
            if fecha:
                texto += f" - {fecha}"
            texto += "\n"
        
        return texto
    
    def _formatear_historial(self, historial: List[Dict], nombre_local: str, nombre_visitante: str) -> str:
        """Formatea el historial de enfrentamientos"""
        if not historial:
            return "No hay historial de enfrentamientos disponible"
        
        texto = ""
        for i, enfrentamiento in enumerate(historial[:5], 1):  # Últimos 5 enfrentamientos
            fecha = enfrentamiento.get('fecha', '')
            resultado = enfrentamiento.get('resultado', '')
            texto += f"{i}. {resultado} - {fecha}\n"
        
        return texto
    
    def _formatear_tabla_posiciones(self, tabla: List[Dict]) -> str:
        """Formatea la tabla de posiciones"""
        if not tabla:
            return "Tabla de posiciones no disponible"
        
        texto = "Pos | Equipo | Pts | PJ | V | E | D | GF | GC | DG\n"
        texto += "-" * 60 + "\n"
        
        for equipo in tabla[:10]:  # Top 10
            pos = equipo.get('posicion', 0)
            nombre = equipo.get('equipo', 'N/A')
            pts = equipo.get('puntos', 0)
            pj = equipo.get('partidos_jugados', 0)
            v = equipo.get('victorias', 0)
            e = equipo.get('empates', 0)
            d = equipo.get('derrotas', 0)
            gf = equipo.get('goles_favor', 0)
            gc = equipo.get('goles_contra', 0)
            dg = equipo.get('diferencia_goles', 0)
            
            texto += f"{pos:3d} | {nombre[:20]:20s} | {pts:3d} | {pj:2d} | {v:2d} | {e:2d} | {d:2d} | {gf:2d} | {gc:2d} | {dg:+3d}\n"
        
        return texto
    
    def _procesar_respuesta(self, respuesta: str, partido_data: Dict) -> Dict:
        """Procesa la respuesta de Gemini y extrae la información"""
        try:
            # Limpiar la respuesta de posibles markdown o código
            respuesta_limpia = respuesta.strip()
            
            # Remover markdown code blocks si existen
            respuesta_limpia = re.sub(r'```json\s*', '', respuesta_limpia)
            respuesta_limpia = re.sub(r'```\s*', '', respuesta_limpia)
            
            # Intentar encontrar JSON en la respuesta
            # Buscar el primer { y el último }
            inicio = respuesta_limpia.find('{')
            fin = respuesta_limpia.rfind('}')
            
            if inicio != -1 and fin != -1 and fin > inicio:
                json_str = respuesta_limpia[inicio:fin+1]
                data = json.loads(json_str)
                
                # Validar y extraer datos
                goles_local = int(data.get('goles_local', 1))
                goles_visitante = int(data.get('goles_visitante', 1))
                analisis = data.get('analisis', respuesta_limpia)
                confianza = float(data.get('confianza', 50.0))
                
                # Asegurar valores razonables
                goles_local = max(0, min(goles_local, 10))  # Entre 0 y 10
                goles_visitante = max(0, min(goles_visitante, 10))
                confianza = max(0.0, min(confianza, 100.0))
                
                return {
                    'goles_local': goles_local,
                    'goles_visitante': goles_visitante,
                    'analisis': analisis.strip(),
                    'confianza': round(confianza, 2)
                }
        except json.JSONDecodeError as e:
            logger.warning(f"Error parseando JSON de Gemini: {e}. Respuesta: {respuesta[:200]}")
        except Exception as e:
            logger.warning(f"Error procesando respuesta de Gemini: {e}")
        
        # Fallback: intentar extraer números del texto
        try:
            numeros = re.findall(r'\b\d+\b', respuesta)
            if len(numeros) >= 2:
                goles_local = int(numeros[0])
                goles_visitante = int(numeros[1])
                # Buscar confianza (número seguido de % o cerca de palabras como "confianza")
                confianza = 50.0
                for i, num in enumerate(numeros):
                    if i > 0 and (respuesta.lower().find('confianza') != -1 or respuesta.lower().find('%') != -1):
                        try:
                            conf = float(num)
                            if 0 <= conf <= 100:
                                confianza = conf
                                break
                        except:
                            pass
                
                return {
                    'goles_local': max(0, min(goles_local, 10)),
                    'goles_visitante': max(0, min(goles_visitante, 10)),
                    'analisis': respuesta.strip(),
                    'confianza': round(confianza, 2)
                }
        except Exception as e:
            logger.error(f"Error en fallback de procesamiento: {e}")
        
        # Último recurso: valores por defecto
        return {
            'goles_local': 1,
            'goles_visitante': 1,
            'analisis': respuesta.strip() if respuesta else 'No se pudo generar análisis',
            'confianza': 50.0
        }

