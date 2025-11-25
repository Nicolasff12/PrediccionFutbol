"""
Utilidades para cálculos de estadísticas y probabilidades
"""
from typing import Dict, List, Optional
from django.db.models import Q, Count, Avg, Sum, F
from django.db import models
from datetime import datetime, timedelta
from .models import Partido, Equipo, Liga
import logging

logger = logging.getLogger(__name__)


def calcular_estadisticas_equipo(equipo: Equipo, liga: Liga = None) -> Dict:
    """
    Calcula estadísticas de un equipo basadas en partidos históricos de la BD local
    """
    try:
        # Filtrar partidos del equipo
        partidos_local = Partido.objects.filter(
            equipo_local=equipo,
            estado='FT'
        )
        partidos_visitante = Partido.objects.filter(
            equipo_visitante=equipo,
            estado='FT'
        )
        
        if liga:
            partidos_local = partidos_local.filter(liga=liga)
            partidos_visitante = partidos_visitante.filter(liga=liga)
        
        # Estadísticas como local
        total_local = partidos_local.count()
        victorias_local = partidos_local.filter(goles_local__gt=F('goles_visitante')).count()
        empates_local = partidos_local.filter(goles_local=F('goles_visitante')).count()
        derrotas_local = partidos_local.filter(goles_local__lt=F('goles_visitante')).count()
        goles_favor_local = partidos_local.aggregate(Sum('goles_local'))['goles_local__sum'] or 0
        goles_contra_local = partidos_local.aggregate(Sum('goles_visitante'))['goles_visitante__sum'] or 0
        
        # Estadísticas como visitante
        total_visitante = partidos_visitante.count()
        victorias_visitante = partidos_visitante.filter(goles_visitante__gt=F('goles_local')).count()
        empates_visitante = partidos_visitante.filter(goles_visitante=F('goles_local')).count()
        derrotas_visitante = partidos_visitante.filter(goles_visitante__lt=F('goles_local')).count()
        goles_favor_visitante = partidos_visitante.aggregate(Sum('goles_visitante'))['goles_visitante__sum'] or 0
        goles_contra_visitante = partidos_visitante.aggregate(Sum('goles_local'))['goles_local__sum'] or 0
        
        # Totales
        total_partidos = total_local + total_visitante
        total_victorias = victorias_local + victorias_visitante
        total_empates = empates_local + empates_visitante
        total_derrotas = derrotas_local + derrotas_visitante
        total_goles_favor = goles_favor_local + goles_favor_visitante
        total_goles_contra = goles_contra_local + goles_contra_visitante
        
        # Promedios
        promedio_goles_favor = total_goles_favor / total_partidos if total_partidos > 0 else 0
        promedio_goles_contra = total_goles_contra / total_partidos if total_partidos > 0 else 0
        
        # Porcentajes
        porcentaje_victorias = (total_victorias / total_partidos * 100) if total_partidos > 0 else 0
        porcentaje_empates = (total_empates / total_partidos * 100) if total_partidos > 0 else 0
        porcentaje_derrotas = (total_derrotas / total_partidos * 100) if total_partidos > 0 else 0
        
        return {
            'total_partidos': total_partidos,
            'victorias': total_victorias,
            'empates': total_empates,
            'derrotas': total_derrotas,
            'goles_favor': total_goles_favor,
            'goles_contra': total_goles_contra,
            'diferencia_goles': total_goles_favor - total_goles_contra,
            'promedio_goles_favor': round(promedio_goles_favor, 2),
            'promedio_goles_contra': round(promedio_goles_contra, 2),
            'porcentaje_victorias': round(porcentaje_victorias, 1),
            'porcentaje_empates': round(porcentaje_empates, 1),
            'porcentaje_derrotas': round(porcentaje_derrotas, 1),
            # Como local
            'local': {
                'partidos': total_local,
                'victorias': victorias_local,
                'empates': empates_local,
                'derrotas': derrotas_local,
                'goles_favor': goles_favor_local,
                'goles_contra': goles_contra_local,
            },
            # Como visitante
            'visitante': {
                'partidos': total_visitante,
                'victorias': victorias_visitante,
                'empates': empates_visitante,
                'derrotas': derrotas_visitante,
                'goles_favor': goles_favor_visitante,
                'goles_contra': goles_contra_visitante,
            }
        }
    except Exception as e:
        logger.error(f"Error calculando estadísticas de {equipo}: {e}")
        return {}


def calcular_forma_equipo(equipo: Equipo, liga: Liga = None, limite: int = 5) -> str:
    """
    Calcula la forma reciente de un equipo (últimos N partidos)
    Retorna string como 'WWDLW' (Win, Win, Draw, Loss, Win)
    """
    try:
        # Obtener últimos partidos del equipo
        partidos = Partido.objects.filter(
            Q(equipo_local=equipo) | Q(equipo_visitante=equipo),
            estado='FT'
        ).order_by('-fecha')[:limite]
        
        if liga:
            partidos = partidos.filter(liga=liga)
        
        forma = []
        for partido in partidos:
            if partido.equipo_local == equipo:
                if partido.goles_local > partido.goles_visitante:
                    forma.append('W')
                elif partido.goles_local < partido.goles_visitante:
                    forma.append('L')
                else:
                    forma.append('D')
            else:  # equipo_visitante
                if partido.goles_visitante > partido.goles_local:
                    forma.append('W')
                elif partido.goles_visitante < partido.goles_local:
                    forma.append('L')
                else:
                    forma.append('D')
        
        return ''.join(forma) if forma else 'N/A'
    except Exception as e:
        logger.error(f"Error calculando forma de {equipo}: {e}")
        return 'N/A'


def calcular_probabilidades_partido(partido: Partido) -> Dict[str, float]:
    """
    Calcula probabilidades de un partido basado en estadísticas históricas
    """
    try:
        equipo_local = partido.equipo_local
        equipo_visitante = partido.equipo_visitante
        liga = partido.liga
        
        # Obtener estadísticas de ambos equipos
        stats_local = calcular_estadisticas_equipo(equipo_local, liga)
        stats_visitante = calcular_estadisticas_equipo(equipo_visitante, liga)
        
        # Si no hay datos suficientes, usar probabilidades por defecto
        if not stats_local or not stats_visitante or stats_local.get('total_partidos', 0) == 0:
            return {'local': 40.0, 'empate': 30.0, 'visitante': 30.0}
        
        # Factores para calcular probabilidades
        # 1. Factor de rendimiento general (victorias)
        factor_local = stats_local.get('porcentaje_victorias', 0) / 100
        factor_visitante = stats_visitante.get('porcentaje_victorias', 0) / 100
        
        # 2. Factor de goles (promedio de goles a favor vs contra)
        factor_goles_local = stats_local.get('promedio_goles_favor', 0) - stats_visitante.get('promedio_goles_contra', 0)
        factor_goles_visitante = stats_visitante.get('promedio_goles_favor', 0) - stats_local.get('promedio_goles_contra', 0)
        
        # 3. Factor de localía (ventaja de jugar en casa)
        ventaja_local = 0.15  # 15% de ventaja por jugar en casa
        
        # 4. Factor de forma reciente
        forma_local = calcular_forma_equipo(equipo_local, liga, 5)
        forma_visitante = calcular_forma_equipo(equipo_visitante, liga, 5)
        
        factor_forma_local = (forma_local.count('W') * 0.1) - (forma_local.count('L') * 0.1)
        factor_forma_visitante = (forma_visitante.count('W') * 0.1) - (forma_visitante.count('L') * 0.1)
        
        # Calcular probabilidades base
        prob_local_base = 0.33 + (factor_local * 0.2) + (factor_goles_local * 0.05) + ventaja_local + factor_forma_local
        prob_visitante_base = 0.33 + (factor_visitante * 0.2) + (factor_goles_visitante * 0.05) + factor_forma_visitante
        prob_empate_base = 0.34 - (abs(factor_local - factor_visitante) * 0.1)
        
        # Asegurar valores mínimos
        prob_local_base = max(0.1, prob_local_base)
        prob_visitante_base = max(0.1, prob_visitante_base)
        prob_empate_base = max(0.1, prob_empate_base)
        
        # Normalizar para que sumen 100%
        total = prob_local_base + prob_visitante_base + prob_empate_base
        
        return {
            'local': round((prob_local_base / total) * 100, 1),
            'empate': round((prob_empate_base / total) * 100, 1),
            'visitante': round((prob_visitante_base / total) * 100, 1)
        }
    except Exception as e:
        logger.error(f"Error calculando probabilidades para {partido}: {e}")
        return {'local': 40.0, 'empate': 30.0, 'visitante': 30.0}

