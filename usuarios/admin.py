from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


# Register your models here.
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'tipo']
    list_filter = ['tipo', 'is_staff', 'is_active']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('tipo', 'telefono', 'fecha_nacimiento')
        }),
    )