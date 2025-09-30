from django.contrib import admin
from .models import Turno, DisponibilidadHoraria

# Register your models here.
@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'fecha', 'hora', 'estado']
    list_filter = ['estado', 'fecha']
    search_fields = ['paciente__usuario__first_name', 'paciente__usuario__last_name']
    date_hierarchy = 'fecha'

@admin.register(DisponibilidadHoraria)
class DisponibilidadHorariaAdmin(admin.ModelAdmin):
    list_display = ['dia_semana', 'hora_inicio', 'hora_fin', 'activo']
    list_filter = ['dia_semana', 'activo']