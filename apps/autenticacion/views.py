from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .forms import RegistroForm, PerfilForm, LoginForm
from .models import Usuario


@csrf_protect
def registro_view(request):
    """Vista para registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('partidos:landing')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '¡Registro exitoso! Por favor inicia sesión.')
            return redirect('auth:login')
    else:
        form = RegistroForm()
    
    return render(request, 'autenticacion/registro.html', {'form': form})


@csrf_protect
def login_view(request):
    """Vista para login de usuarios"""
    if request.user.is_authenticated:
        return redirect('partidos:landing')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido, {user.get_full_name() or user.username}!')
                return redirect('partidos:landing')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'autenticacion/login.html', {'form': form})


@login_required
def perfil_view(request):
    """Vista para ver y editar perfil"""
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('auth:perfil')
    else:
        form = PerfilForm(instance=request.user)
    
    return render(request, 'autenticacion/perfil.html', {'form': form})

