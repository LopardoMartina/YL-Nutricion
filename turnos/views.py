from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Turno, DisponibilidadHoraria
from calendar import monthcalendar, month_name
from datetime import datetime, timedelta
from pacientes.models import Paciente
from django.db.models import Q, Count
from django.contrib import messages
from django.utils import timezone
import calendar as cal
import json

# Create your views here.
@login_required
def agendar_turno_view(request):
    """Vista para agendar turnos con calendario interactivo"""
    
    # Verificar que el usuario sea paciente
    if request.user.tipo != 'paciente':
        messages.error(request, 'Solo los pacientes pueden agendar turnos.')
        return redirect('core:home')
    
    # Obtener o crear el perfil de paciente
    paciente, created = Paciente.objects.get_or_create(usuario=request.user)
    
    # Obtener disponibilidades activas
    #disponibilidades = DisponibilidadHoraria.objects.filter(activo=True)
    
    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        motivo = request.POST.get('motivo', '')
        
        # Validar que se haya seleccionado fecha y hora
        if not fecha or not hora:
            messages.error(request, "Debes seleccionar una fecha y una hora antes de confirmar el turno.")
            return redirect('turnos:agendar')
        
        # Validar que no exista un turno en ese horario
        if Turno.objects.filter(fecha=fecha, hora=hora).exclude(estado='cancelado').exists():
            messages.error(request, 'Este horario ya está ocupado. Por favor elige otro.')
            return redirect('turnos:agendar')
        
        # Crear el turno
        Turno.objects.create(
            paciente=paciente,
            fecha=fecha,
            hora=hora,
            motivo=motivo,
            estado='pendiente'
        )
        
        messages.success(request, f'Turno agendado exitosamente para el {fecha} a las {hora}.')
        return redirect('turnos:mis_turnos')
    
    # Obtener disponibilidades activas
    disponibilidades = list(DisponibilidadHoraria.objects.filter(activo=True).values(
        'dia_semana', 'hora_inicio', 'hora_fin'
    ))
    
    # Convertir time objects a strings para JSON
    for disp in disponibilidades:
        disp['hora_inicio'] = disp['hora_inicio'].strftime('%H:%M')
        disp['hora_fin'] = disp['hora_fin'].strftime('%H:%M')
    
    # Generar horarios disponibles para los próximos 30 días
    fecha_actual = datetime.now().date()
    fecha_limite = fecha_actual + timedelta(days=30)
    
    turnos_ocupados = list(Turno.objects.filter(
        fecha__gte=fecha_actual,
        fecha__lte=fecha_limite
    ).exclude(estado='cancelado').values('fecha', 'hora'))
    
    
    #Convertir fechas a strings
    for turno in turnos_ocupados:
        turno['fecha'] = turno['fecha'].isoformat()
        turno['hora'] = turno['hora'].strftime('%H:%M')
    
    
    #turnos futuros del pacientes
    turnos_futuros = Turno.objects.filter(
        paciente=paciente,
        fecha__gte=fecha_actual
    ).exclude(estado='cancelado').order_by('fecha', 'hora')
    
    
    context = {
        'disponibilidades': json.dumps(disponibilidades),
        'turnos_ocupados': json.dumps(turnos_ocupados),
        'turnos_futuros': turnos_futuros,
    }
    
    return render(request, 'turnos/agendar_turno.html', context)


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
    
    # Obtener mes y año de la URL o usar el actual
    mes = int(request.GET.get('mes', datetime.now().month))
    anio = int(request.GET.get('anio', datetime.now().year))
    
    # Obtener todos los turnos del mes
    turnos = Turno.objects.filter(
        fecha__year=anio,
        fecha__month=mes
    ).select_related('paciente__usuario').order_by('fecha', 'hora')
    
    # organizar los turnos por fecha
    turnos_por_fecha = {}
    for turno in turnos:
        fecha_str = turno.fecha.isoformat()
        if fecha_str not in turnos_por_fecha:
            turnos_por_fecha[fecha_str] = []
        turnos_por_fecha[fecha_str].append(turno)
        
    #generar el calendario 
    cal_matrix = monthcalendar(anio, mes)
    
    # mes anterior y el siguiente
    if mes == 1:
        mes_anterior = 12
        anio_anterior = anio - 1
    else:
        mes_anterior = mes - 1
        anio_anterior = anio
    
    if mes == 12:
        mes_siguiente = 1
        anio_siguiente = anio + 1
    else:
        mes_siguiente = mes + 1
        anio_siguiente = anio
        
    context= {
        'mes': mes,
        'anio': anio,
        'mes_nombre': month_name[mes],
        'calendario': cal_matrix,
        'turnos_por_fecha': turnos_por_fecha,
        'mes_anterior': mes_anterior,
        'anio_anterior': anio_anterior,
        'mes_siguiente': mes_siguiente,
        'anio_siguiente': anio_siguiente,
        'hoy': datetime.now().date(),
    }
    return render(request, 'turnos/calendario.html', context)


@login_required
def detalle_turno_view(request, turno_id):
    """
    Vista para ver los detalles de un turno.
    """
    if request.user.tipo != 'profesional':
        messages.error(request, 'Acceso denegado.')
        return redirect('core:home')

    turno = get_object_or_404(Turno, id=turno_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'confirmar':
            turno.estado = 'confirmado'
            turno.save()
            messages.success(request, 'Turno confirmado.')
        
        elif action == 'completar':
            turno.estado = 'completado'
            turno.notas_profesional = request.POST.get('notas', '')
            turno.save()
            messages.success(request, 'Turno marcado como completado.')
            
        elif action == 'cancelar':
            turno.estado = 'cancelado'
            turno.save()
            messages.success(request, 'Turno cancelado.')
        
        return redirect('turnos:calendario')
    
    context ={
        'turno': turno,
        'paciente': turno.paciente,
    }
    
    return render(request, 'turnos/detalle_turno.html', context)
    

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
        
        action = request.POST.get('action')
        
        if action == 'agregar':
            dia_semana = request.POST.get('dia_semana')
            hora_inicio = request.POST.get('hora_inicio')
            hora_fin = request.POST.get('hora_fin')
            
            DisponibilidadHoraria.objects.create(
                dia_semana=dia_semana,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                activo = True
            )
            messages.success(request, 'Disponibilidad agregada correctamente.')
            
        elif action == 'eliminar':
            disp_id = request.POST.get('disp_id')
            DisponibilidadHoraria.objects.filter(id=disp_id).delete()
            messages.success(request, 'Disponibilidad eliminada correctamente.')
            
        elif action == 'toggle':
            disp_id = request.POST.get('disp_id')
            disp = DisponibilidadHoraria.objects.get(id=disp_id)
            disp.activo = not disp.activo
            disp.save()
            messages.success(request, f'Disponibilidad {"activada" if disp.activo else "desactivada"}.')
    
        return redirect('turnos:disponibilidad')
    
    dias_semana =[
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    context = {
        'disponibilidades': disponibilidades,
        'dias_semana': dias_semana
    }
    
    return render(request, 'turnos/disponibilidad.html', context)