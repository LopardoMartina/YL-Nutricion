from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    #path('', views.index_view, name='index'),
    #path('contacto/', views.contacto_view, name='contacto'),
    path('', views.home_view, name='home'),
]