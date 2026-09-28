from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .forms import RestringidoPasswordResetForm

app_name = 'usuarios'

urlpatterns = [
    path('', views.vista_login, name='login'),
    path('login/', views.vista_login, name='login_alt'),
    path('logout/', views.vista_logout, name='logout'),

    path('dashboard/', views.vista_dashboard, name='dashboard'),

    path('usuarios/', views.vista_gestion_usuarios, name='gestion_usuarios'),
    path('usuarios/nuevo/', views.vista_crear_usuario, name='crear_usuario'),
    path('usuarios/<int:usuario_id>/asignar-rol/', views.vista_asignar_rol, name='asignar_rol'),

    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            form_class=RestringidoPasswordResetForm,
            template_name='usuarios/password_reset_form.html',
            email_template_name='usuarios/password_reset_email.html',
            subject_template_name='usuarios/password_reset_subject.txt',
            success_url=reverse_lazy('usuarios:password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'password-reset/hecho/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='usuarios/password_reset_done.html'
        ),
        name='password_reset_done',
    ),
    path(
        'password-reset-confirmar/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='usuarios/password_reset_confirm.html',
            success_url=reverse_lazy('usuarios:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'password-reset-completo/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='usuarios/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),
]