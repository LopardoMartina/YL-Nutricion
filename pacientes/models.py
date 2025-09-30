from django.db import models
from django.conf import settings

# Create your models here.
class Paciente(models.Model):
    """
    Información adicional del paciente.
    Está vinculado 1-a-1 con el Usuario.
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='paciente'
    )
    
    # Datos médicos
    altura = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Altura en metros (ej: 1.75)"
    )
    peso_actual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Peso en kilogramos"
    )
    
    # Historial médico
    alergias = models.TextField(blank=True)
    medicamentos = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['usuario__last_name', 'usuario__first_name']
    
    def __str__(self):
        return f"Paciente: {self.usuario.get_full_name()}"


class RegistroHistorial(models.Model):
    """
    Registro histórico de cada consulta o medición del paciente.
    """
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='historial'
    )
    
    fecha = models.DateField()
    peso = models.DecimalField(max_digits=5, decimal_places=2)
    notas = models.TextField(blank=True)
    
    # Campos adicionales opcionales
    circunferencia_cintura = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    circunferencia_cadera = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Registro de Historial'
        verbose_name_plural = 'Registros de Historial'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.paciente} - {self.fecha}"