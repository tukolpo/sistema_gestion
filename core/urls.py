"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Integrante 1: Rutas del módulo Login y Gestión de Usuarios
    path('', include('usuarios.urls', namespace='usuarios')),
]
