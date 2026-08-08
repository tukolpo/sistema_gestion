# usuarios/urls.py
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
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<int:usuario_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:usuario_id>/cambiar-password/', views.cambiar_password, name='cambiar_password'),
    path('usuarios/<int:usuario_id>/asignar-rol/', views.vista_asignar_rol, name='asignar_rol'),

    # ─── Auditoría ───────────────────────────────────────────────
    path('auditoria/', views.vista_auditoria, name='auditoria'),

    # ─── Roles y Permisos ────────────────────────────────────────
    path('roles/', views.lista_roles, name='lista_roles'),
    path('roles/crear/', views.crear_rol, name='crear_rol'),
    path('roles/<int:rol_id>/editar/', views.editar_rol, name='editar_rol'),
    path('roles/<int:rol_id>/eliminar/', views.eliminar_rol, name='eliminar_rol'),
]
