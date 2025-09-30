from django.contrib import admin
from .models import Paciente, RegistroHistorial

# Register your models here.
class RegistroHistorialInline(admin.TabularInline):
    model = RegistroHistorial
    extra = 0

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'peso_actual', 'altura', 'fecha_actualizacion']
    search_fields = ['usuario__first_name', 'usuario__last_name', 'usuario__email']
    inlines = [RegistroHistorialInline]

@admin.register(RegistroHistorial)
class RegistroHistorialAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'fecha', 'peso']
    list_filter = ['fecha']
    date_hierarchy = 'fecha'