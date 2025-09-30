from django.db import models
from django.conf import settings
from pacientes.models import Paciente

# Create your models here.

class Turno(models.Model):
    """
    Representa un turno/cita médica.
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
        ('completado', 'Completado'),
    ]
    
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='turnos'
    )
    
    fecha = models.DateField()
    hora = models.TimeField()
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    
    motivo = models.CharField(max_length=200, blank=True)
    notas_profesional = models.TextField(blank=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['fecha', 'hora']
        # Evita que se agenden dos turnos a la misma hora
        unique_together = ['fecha', 'hora']
    
    def __str__(self):
        return f"{self.paciente} - {self.fecha} {self.hora}"


class DisponibilidadHoraria(models.Model):
    """
    Define qué días y horas el profesional está disponible.
    """
    DIAS_SEMANA = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]
    
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Disponibilidad Horaria'
        verbose_name_plural = 'Disponibilidades Horarias'
        ordering = ['dia_semana', 'hora_inicio']
    
    def __str__(self):
        return f"{self.get_dia_semana_display()}: {self.hora_inicio} - {self.hora_fin}"