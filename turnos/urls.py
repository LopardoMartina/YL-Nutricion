from django.urls import path
from . import views

app_name = 'turnos'

urlpatterns = [
    # URLs para pacientes
    path('agendar/', views.agendar_turno_view, name='agendar'),
    path('mis-turnos/', views.mis_turnos_view, name='mis_turnos'),
    path('cancelar/<int:turno_id>/', views.cancelar_turno_view, name='cancelar'),
    
    # URLs para profesional
    path('calendario/', views.calendario_view, name='calendario'),
    path('turno/<int:turno_id>/', views.detalle_turno_view, name='detalle_turno'),
    path('disponibilidad/', views.disponibilidad_view, name='disponibilidad'),
]