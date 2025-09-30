from django.urls import path
from . import views

app_name = 'pacientes'

urlpatterns = [
    path('', views.lista_pacientes_view, name='lista'),
    #path('<int:paciente_id>/', views.detalle_paciente_view, name='detalle'),
]