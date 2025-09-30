from django.shortcuts import render, get_object_or_404
from .models import Paciente

# Create your views here.
def lista_pacientes_view(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    return render(request, 'pacientes/detalle.html', {'paciente': paciente})