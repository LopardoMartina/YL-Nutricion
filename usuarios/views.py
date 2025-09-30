from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import RegistroForm, LoginForm

# Create your views here.
def registro_view(request):
    """
    Vista para registro de nuevos pacientes.
    """
    # Si el usuario ya está logueado, redirigir al inicio
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Loguear automáticamente al usuario después de registrarse
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido a Nutrición YL.')
            return redirect('core:home')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})


def login_view(request):
    """
    Vista para inicio de sesión.
    """
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de nuevo, {user.first_name}!')
                
                # Redirigir según el tipo de usuario
                if user.tipo == 'profesional':
                    return redirect('turnos:calendario')
                else:
                    # Redirigir a donde el usuario quería ir (o al inicio)
                    next_url = request.GET.get('next', 'core:home')
                    return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})


def logout_view(request):
    """
    Vista para cerrar sesión.
    """
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('core:home')


@login_required
def perfil_view(request):
    """
    Vista del perfil del usuario.
    Solo accesible para usuarios autenticados.
    """
    # Si es paciente, obtener su información adicional
    paciente = None
    if request.user.tipo == 'paciente':
        paciente = request.user.paciente
    
    context = {
        'usuario': request.user,
        'paciente': paciente
    }
    
    return render(request, 'usuarios/perfil.html', context)