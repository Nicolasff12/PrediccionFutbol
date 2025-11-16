from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .controllers import PartidoController

partido_controller = PartidoController()


@login_required
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
        return redirect('partidos:home')
    
    return redirect('partidos:home')

