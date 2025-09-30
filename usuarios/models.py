from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Usuario(AbstractUser):
    """
    Usuario personalizado que extiende el usuario de Django.
    Permite agregar campos adicionales específicos del proyecto.
    """
    TIPO_CHOICES = [
        ('paciente', 'Paciente'),
        ('profesional', 'Profesional'),
    ]
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='paciente'
    )
    telefono = models.CharField(max_length=20, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_tipo_display()})"