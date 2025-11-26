from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .controllers import PartidoController
from .models import Equipo, Liga
# from .services.estadisticas_calculadas import EstadisticasCalculadas  # Deshabilitado temporalmente
import logging

logger = logging.getLogger(__name__)

partido_controller = PartidoController()


def landing_view(request):
    """Vista de landing page - Página de inicio con información de la aplicación"""
    return render(request, 'partidos/landing.html')


def home_view(request):
    """Vista principal con todos los datos importantes de partidos"""
    # Obtener datos del controlador
    partidos_proximos = partido_controller.obtener_partidos_proximos(limite=10)
    partidos_recientes = partido_controller.obtener_partidos_recientes(limite=10)
    partidos_hoy = partido_controller.obtener_partidos_hoy()
    estadisticas = partido_controller.obtener_estadisticas_liga()
    
    context = {
        'partidos_proximos': partidos_proximos,
        'partidos_recientes': partidos_recientes,
        'partidos_hoy': partidos_hoy,
        'estadisticas': estadisticas,
    }
    
    return render(request, 'partidos/home.html', context)


@login_required
def sincronizar_partidos_view(request):
    """Vista para sincronizar partidos desde la API"""
    if request.method == 'POST':
        exito = partido_controller.sincronizar_liga_betplay()
        if exito:
            messages.success(request, 'Partidos sincronizados correctamente.')
        else:
            messages.error(request, 'Error al sincronizar partidos. Verifique la configuración de la API.')
        return redirect('partidos:landing')
    
    return redirect('partidos:landing')


@login_required
def detalle_equipo_view(request, equipo_id):
    """Vista de detalle de un equipo con estadísticas y partidos"""
    equipo = get_object_or_404(Equipo, id=equipo_id)
    
    # Obtener liga (asumimos que todos los equipos están en la misma liga por ahora)
    liga = Liga.objects.filter(id_api=50).first() or Liga.objects.first()
    
    # Obtener estadísticas calculadas (deshabilitado temporalmente)
    estadisticas = None
    ultimos_partidos = []
    proximos_partidos_equipo = []
    
    # if liga:
    #     try:
    #         estadisticas = EstadisticasCalculadas.obtener_estadisticas_equipo(equipo, liga)
    #         ultimos_partidos = EstadisticasCalculadas.obtener_ultimos_partidos_equipo(equipo, liga, limite=10)
    #     except Exception as e:
    #         logger.warning(f"Error calculando estadísticas: {e}")
    
    # Obtener próximos partidos del equipo
    if liga:
        from datetime import datetime
        from django.db.models import Q
        from .models import Partido
        
        try:
            proximos_partidos_equipo = Partido.objects.filter(
                liga=liga
            ).filter(
                Q(equipo_local=equipo) | Q(equipo_visitante=equipo)
            ).filter(
                estado__in=['NS', 'LIVE'],
                fecha__gte=datetime.now()
            ).order_by('fecha')[:5]
        except Exception as e:
            logger.warning(f"Error obteniendo próximos partidos: {e}")
            proximos_partidos_equipo = []
    
    context = {
        'equipo': equipo,
        'liga': liga,
        'estadisticas': estadisticas,
        'ultimos_partidos': ultimos_partidos,
        'proximos_partidos': proximos_partidos_equipo,
    }
    
    return render(request, 'partidos/detalle_equipo.html', context)


@login_required
def lista_equipos_view(request):
    """Vista para listar todos los equipos con búsqueda y filtros"""
    equipos = Equipo.objects.exclude(nombre='').order_by('nombre')
    
    # Búsqueda
    busqueda = request.GET.get('q', '')
    if busqueda:
        equipos = equipos.filter(nombre__icontains=busqueda)
    
    # Obtener liga para calcular estadísticas
    liga = Liga.objects.filter(id_api=50).first() or Liga.objects.first()
    
    # Agregar estadísticas básicas a cada equipo (deshabilitado temporalmente)
    equipos_con_stats = []
    for equipo in equipos:
        stats = None
        # if liga:
        #     try:
        #         stats = EstadisticasCalculadas.obtener_estadisticas_equipo(equipo, liga)
        #     except Exception as e:
        #         logger.warning(f"Error calculando estadísticas para {equipo}: {e}")
        
        equipos_con_stats.append({
            'equipo': equipo,
            'estadisticas': stats
        })
    
    context = {
        'equipos': equipos_con_stats,
        'busqueda': busqueda,
        'liga': liga,
    }
    
    return render(request, 'partidos/lista_equipos.html', context)


@login_required
def comparar_equipos_view(request):
    """Vista para comparar dos equipos"""
    equipo1_id = request.GET.get('equipo1')
    equipo2_id = request.GET.get('equipo2')
    
    # Obtener todos los equipos para el selector
    todos_equipos = Equipo.objects.exclude(nombre='').order_by('nombre')
    
    # Obtener liga
    liga = Liga.objects.filter(id_api=50).first() or Liga.objects.first()
    
    equipo1 = None
    equipo2 = None
    estadisticas1 = None
    estadisticas2 = None
    ultimos_partidos1 = []
    ultimos_partidos2 = []
    historial_enfrentamientos = []
    proximo_enfrentamiento = None
    
    if equipo1_id and equipo2_id:
        try:
            equipo1 = Equipo.objects.get(id=equipo1_id)
            equipo2 = Equipo.objects.get(id=equipo2_id)
            
            if liga:
                # Obtener estadísticas (deshabilitado temporalmente)
                estadisticas1 = None
                estadisticas2 = None
                ultimos_partidos1 = []
                ultimos_partidos2 = []
                historial_enfrentamientos = []
                
                # try:
                #     estadisticas1 = EstadisticasCalculadas.obtener_estadisticas_equipo(equipo1, liga)
                #     estadisticas2 = EstadisticasCalculadas.obtener_estadisticas_equipo(equipo2, liga)
                #     ultimos_partidos1 = EstadisticasCalculadas.obtener_ultimos_partidos_equipo(equipo1, liga, limite=5)
                #     ultimos_partidos2 = EstadisticasCalculadas.obtener_ultimos_partidos_equipo(equipo2, liga, limite=5)
                #     historial_enfrentamientos = EstadisticasCalculadas.obtener_historial_enfrentamientos(
                #         equipo1, equipo2, liga, limite=5
                #     )
                # except Exception as e:
                #     logger.warning(f"Error calculando estadísticas de comparación: {e}")
                
                # Buscar próximo enfrentamiento
                from datetime import datetime
                from django.db.models import Q
                from .models import Partido
                
                proximo_enfrentamiento = Partido.objects.filter(
                    liga=liga,
                    estado__in=['NS', 'LIVE'],
                    fecha__gte=datetime.now()
                ).filter(
                    (Q(equipo_local=equipo1) & Q(equipo_visitante=equipo2)) |
                    (Q(equipo_local=equipo2) & Q(equipo_visitante=equipo1))
                ).order_by('fecha').first()
                
        except Equipo.DoesNotExist:
            messages.error(request, 'Uno o ambos equipos no fueron encontrados.')
    
    context = {
        'todos_equipos': todos_equipos,
        'equipo1': equipo1,
        'equipo2': equipo2,
        'estadisticas1': estadisticas1,
        'estadisticas2': estadisticas2,
        'ultimos_partidos1': ultimos_partidos1,
        'ultimos_partidos2': ultimos_partidos2,
        'historial_enfrentamientos': historial_enfrentamientos,
        'proximo_enfrentamiento': proximo_enfrentamiento,
        'liga': liga,
    }
    
    return render(request, 'partidos/comparar_equipos.html', context)