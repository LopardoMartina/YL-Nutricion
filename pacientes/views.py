from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from .models import Paciente, RegistroHistorial
from turnos.models import Turno

# Create your views here.
@login_required
def lista_pacientes_view(request):
    """ Lista de todos los pacientes"""
    if request.user.tipo != 'profesional':
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('core:home')
    
    pacientes = Paciente.objects.select_related('usuario').all()
    
    context = {
        'pacientes' : pacientes
    }
    return render(request, 'pacientes/lista.html', context)



@login_required
def detalle_paciente_view(request, paciente_id):
    """ Detalle de un paciente específico """
    if request.user.tipo != 'profesional':
        messages.error(request, "Acceso denegado.")
        return redirect('core:home')
    
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # agregar un nuevo registro
    if request.method == 'POST':
        RegistroHistorial.objects.create(
            paciente=paciente,
            fecha=request.POST.get('fecha'),
            peso=request.POST.get('peso'),
            notas=request.POST.get('notas', ''),
            circunferencia_cintura=request.POST.get('cintura') or None,
            circunferencia_cadera=request.POST.get('caderaS') or None,
        )
        messages.success(request, "Registro agregado exitosamente.")
        return redirect('pacientes:detalle', paciente_id=paciente.id)
    
    historial = paciente.historial.all()
    turnos = paciente.turnos.all().order_by('-fecha', '-hora')
    
    context = {
        'paciente': paciente,
        'historial': historial,
        'turnos': turnos,
    }
    
    return render(request, 'pacientes/detalle.html', context)
    