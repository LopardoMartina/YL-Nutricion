from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Turno, DisponibilidadHoraria
from pacientes.models import Paciente
from datetime import datetime, timedelta, time
from django.db.models import Q

# Create your views here.
@login_required
def agendar_turno_view(request):
    """
    Vista para que los pacientes agenden turnos.
    Muestra horarios disponibles según la configuración del profesional.
    """
    # Verificar que el usuario sea paciente
    if request.user.tipo != 'paciente':
        messages.error(request, 'Solo los pacientes pueden agendar turnos.')
        return redirect('core:home')
    
    # Obtener o crear el perfil de paciente
    paciente, created = Paciente.objects.get_or_create(usuario=request.user)
    
    # Obtener disponibilidades activas
    disponibilidades = DisponibilidadHoraria.objects.filter(activo=True)
    
    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        motivo = request.POST.get('motivo', '')
        
        # Validar que no exista un turno en ese horario
        if Turno.objects.filter(fecha=fecha, hora=hora).exists():
            messages.error(request, 'Este horario ya está ocupado. Por favor elige otro.')
        else:
            # Crear el turno
            turno = Turno.objects.create(
                paciente=paciente,
                fecha=fecha,
                hora=hora,
                motivo=motivo,
                estado='pendiente'
            )
            messages.success(request, f'Turno agendado exitosamente para el {fecha} a las {hora}.')
            return redirect('turnos:mis_turnos')
    
    # Generar horarios disponibles para los próximos 30 días
    fecha_actual = datetime.now().date()
    fecha_limite = fecha_actual + timedelta(days=30)
    
    horarios_disponibles = []
    
    # Iterar por cada día
    fecha_iteracion = fecha_actual
    while fecha_iteracion <= fecha_limite:
        dia_semana = fecha_iteracion.weekday()
        
        # Buscar disponibilidades para este día
        disponibilidad_dia = disponibilidades.filter(dia_semana=dia_semana)
        
        for disp in disponibilidad_dia:
            # Generar horarios cada 30 minutos
            hora_actual = datetime.combine(fecha_iteracion, disp.hora_inicio)
            hora_fin = datetime.combine(fecha_iteracion, disp.hora_fin)
            
            while hora_actual < hora_fin:
                # Verificar si el horario está libre
                if not Turno.objects.filter(
                    fecha=fecha_iteracion,
                    hora=hora_actual.time()
                ).exists():
                    horarios_disponibles.append({
                        'fecha': fecha_iteracion,
                        'hora': hora_actual.time(),
                        'dia_nombre': fecha_iteracion.strftime('%A %d/%m/%Y')
                    })
                
                hora_actual += timedelta(minutes=30)
        
        fecha_iteracion += timedelta(days=1)
    
    context = {
        'horarios_disponibles': horarios_disponibles,
        'paciente': paciente
    }
    
    return render(request, 'turnos/agendar_turnos.html', context)


@login_required
def mis_turnos_view(request):
    """
    Vista para que los pacientes vean sus turnos agendados.
    """
    if request.user.tipo != 'paciente':
        messages.error(request, 'Acceso denegado.')
        return redirect('core:home')
    
    paciente = request.user.paciente
    
    # Obtener turnos futuros y pasados
    fecha_actual = datetime.now().date()
    
    turnos_futuros = Turno.objects.filter(
        paciente=paciente,
        fecha__gte=fecha_actual
    ).exclude(estado='cancelado').order_by('fecha', 'hora')
    
    turnos_pasados = Turno.objects.filter(
        paciente=paciente,
        fecha__lt=fecha_actual
    ).order_by('-fecha', '-hora')[:10]  # Últimos 10
    
    context = {
        'turnos_futuros': turnos_futuros,
        'turnos_pasados': turnos_pasados
    }
    
    return render(request, 'turnos/mis_turnos.html', context)


@login_required
def cancelar_turno_view(request, turno_id):
    """
    Vista para cancelar un turno.
    """
    turno = get_object_or_404(Turno, id=turno_id)
    
    # Verificar que el turno pertenece al usuario
    if turno.paciente.usuario != request.user and request.user.tipo != 'profesional':
        messages.error(request, 'No tienes permiso para cancelar este turno.')
        return redirect('turnos:mis_turnos')
    
    if request.method == 'POST':
        turno.estado = 'cancelado'
        turno.save()
        messages.success(request, 'Turno cancelado correctamente.')
        
        if request.user.tipo == 'profesional':
            return redirect('turnos:calendario')
        else:
            return redirect('turnos:mis_turnos')
    
    return render(request, 'turnos/cancelar_turno.html', {'turno': turno})


@login_required
def calendario_view(request):
    """
    Vista del calendario para el profesional.
    Muestra todos los turnos agendados.
    """
    if request.user.tipo != 'profesional':
        messages.error(request, 'Acceso denegado.')
        return redirect('core:home')
    
    # Obtener turnos del mes actual
    fecha_actual = datetime.now()
    turnos = Turno.objects.filter(
        fecha__year=fecha_actual.year,
        fecha__month=fecha_actual.month
    ).select_related('paciente__usuario').order_by('fecha', 'hora')
    
    context = {
        'turnos': turnos,
        'fecha_actual': fecha_actual
    }
    
    return render(request, 'turnos/calendario.html', context)


@login_required
def disponibilidad_view(request):
    """
    Vista para que el profesional configure su disponibilidad horaria.
    """
    if request.user.tipo != 'profesional':
        messages.error(request, 'Acceso denegado.')
        return redirect('core:home')
    
    disponibilidades = DisponibilidadHoraria.objects.all().order_by('dia_semana', 'hora_inicio')
    
    if request.method == 'POST':
        # Lógica para agregar/editar disponibilidad
        dia_semana = request.POST.get('dia_semana')
        hora_inicio = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        
        DisponibilidadHoraria.objects.create(
            dia_semana=dia_semana,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            activo=True
        )
        
        messages.success(request, 'Disponibilidad agregada correctamente.')
        return redirect('turnos:disponibilidad')
    
    context = {
        'disponibilidades': disponibilidades
    }
    
    return render(request, 'turnos/disponibilidad.html', context)