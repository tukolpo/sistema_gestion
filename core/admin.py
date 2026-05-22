# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Rol, Usuario

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nivel_jerarquia', 'fecha_creacion')
    search_fields = ('nombre',)
    ordering = ('-nivel_jerarquia',)

@admin.register(Usuario)
class UsuarioPersonalizadoAdmin(UserAdmin):
    # Añadimos el campo 'rol' y 'cedula' al panel de administración existente de Django
    fieldsets = UserAdmin.fieldsets + (
        ('Información DSI y RBAC', {'fields': ('rol', 'cedula', 'departamento')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_staff')
    list_filter = ('rol', 'is_staff', 'is_superuser')