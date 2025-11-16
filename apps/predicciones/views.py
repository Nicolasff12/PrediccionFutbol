from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from apps.partidos.models import Partido
from apps.predicciones.controllers import PrediccionController
from apps.predicciones.forms import PrediccionForm

prediccion_controller = PrediccionController()


@login_required
def crear_prediccion_view(request, partido_id):
    """Vista para crear una predicción de un partido"""
    partido = get_object_or_404(Partido, id=partido_id)
    
    if request.method == 'POST':
        if 'usar_ia' in request.POST:
            # Crear predicción con IA
            prediccion = prediccion_controller.crear_prediccion_ia(request.user, partido)
            if prediccion:
                messages.success(request, 'Predicción generada con IA exitosamente.')
                return redirect('predicciones:detalle', prediccion_id=prediccion.id)
            else:
                messages.error(request, 'Error al generar predicción con IA.')
        else:
            # Crear predicción manual
            form = PrediccionForm(request.POST)
            if form.is_valid():
                goles_local = form.cleaned_data['goles_local']
                goles_visitante = form.cleaned_data['goles_visitante']
                prediccion = prediccion_controller.crear_prediccion_manual(
                    request.user, partido, goles_local, goles_visitante
                )
                messages.success(request, 'Predicción guardada exitosamente.')
                return redirect('predicciones:detalle', prediccion_id=prediccion.id)
    else:
        form = PrediccionForm()
    
    context = {
        'partido': partido,
        'form': form,
    }
    return render(request, 'predicciones/crear_prediccion.html', context)


@login_required
def mis_predicciones_view(request):
    """Vista para ver todas las predicciones del usuario"""
    predicciones = prediccion_controller.obtener_predicciones_usuario(request.user, limite=20)
    estadisticas = prediccion_controller.obtener_estadisticas_usuario(request.user)
    
    context = {
        'predicciones': predicciones,
        'estadisticas': estadisticas,
    }
    return render(request, 'predicciones/mis_predicciones.html', context)


@login_required
def detalle_prediccion_view(request, prediccion_id):
    """Vista para ver el detalle de una predicción"""
    from apps.predicciones.models import Prediccion
    prediccion = get_object_or_404(Prediccion, id=prediccion_id, usuario=request.user)
    
    context = {
        'prediccion': prediccion,
    }
    return render(request, 'predicciones/detalle_prediccion.html', context)


@login_required
def generar_prediccion_ia_ajax(request, partido_id):
    """Vista AJAX para generar predicción con IA"""
    if request.method == 'POST':
        partido = get_object_or_404(Partido, id=partido_id)
        prediccion = prediccion_controller.crear_prediccion_ia(request.user, partido)
        
        if prediccion:
            return JsonResponse({
                'success': True,
                'goles_local': prediccion.goles_local_predicho,
                'goles_visitante': prediccion.goles_visitante_predicho,
                'analisis': prediccion.prediccion_ia,
                'confianza': prediccion.confianza
            })
        else:
            return JsonResponse({'success': False, 'error': 'Error al generar predicción'})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

