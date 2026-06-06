# usuarios/urls.py
# Integrante 1: Rutas del módulo de login y gestión de usuarios

from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # ─── Autenticación ───────────────────────────────────────────
    path('', views.vista_login, name='login'),
    path('login/', views.vista_login, name='login_alt'),
    path('logout/', views.vista_logout, name='logout'),

    # ─── Panel Principal ─────────────────────────────────────────
    path('dashboard/', views.vista_dashboard, name='dashboard'),

    # ─── Gestión de Usuarios ─────────────────────────────────────
    path('usuarios/', views.vista_gestion_usuarios, name='gestion_usuarios'),
    path('usuarios/<int:usuario_id>/asignar-rol/', views.vista_asignar_rol, name='asignar_rol'),
]
