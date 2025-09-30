from django.shortcuts import render

# Create your views here.
"""
def index_view(request):
    #Página de inicio
    return render(request, 'core/index.html')

def contacto_view(request):
    #Página de contacto
    return render(request, 'core/contacto.html')
"""
def home_view(request):
    """Página de inicio"""
    return render(request, 'core/home.html')