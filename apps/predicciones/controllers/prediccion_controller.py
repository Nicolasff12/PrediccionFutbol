"""
Controlador para manejar la lógica de negocio de predicciones
"""
from typing import Dict, Optional
from django.contrib.auth import get_user_model
from apps.predicciones.models import Prediccion
from apps.predicciones.services import GeminiService
from apps.partidos.models import Partido
import logging

logger = logging.getLogger(__name__)
Usuario = get_user_model()


class PrediccionController:
    """Controlador para gestionar predicciones"""
    
    def __init__(self):
        self.gemini_service = GeminiService()
    
    def crear_prediccion_ia(self, usuario, partido: Partido) -> Optional[Prediccion]:
        """Crea una predicción usando IA para un partido"""
        try:
            # Preparar datos del partido para Gemini
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
                    'nombre': partido.liga.nombre
                },
                'fecha': partido.fecha.isoformat()
            }
            
            # Obtener predicción de Gemini
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
            logger.error(f"Error al crear predicción: {e}")
            return None
    
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

