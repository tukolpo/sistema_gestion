# usuarios/views.py
# Integrante 1: Subtareas 1.1, 1.2, 1.3
# Vistas para Login, Logout y Gestión de Usuarios con manejo de errores visuales.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from core.models import Usuario, Rol
from core.decorators import requiere_jerarquia
from .forms import LoginForm


# ──────────────────────────────────────────────
# Vista 1: Login
# ──────────────────────────────────────────────

def vista_login(request):
    """
    Subtarea 1.1 & 1.3:
    Muestra el formulario de inicio de sesión y maneja errores visuales.
    Si las credenciales son incorrectas, se muestra una alerta al usuario.
    """
    # Si el usuario ya está autenticado, redirigir al dashboard
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Manejar "Recordar contraseña"
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)  # Sesión expira al cerrar navegador

            messages.success(request, f'¡Bienvenido, {user.first_name or user.username}!')
            return redirect('usuarios:dashboard')
        else:
            # La validación del formulario ya incluye los errores de autenticación
            pass

    context = {
        'form': form,
        'titulo': 'Iniciar Sesión',
    }
    return render(request, 'usuarios/login.html', context)


# ──────────────────────────────────────────────
# Vista 2: Logout
# ──────────────────────────────────────────────

@login_required
def vista_logout(request):
    """Cierra la sesión del usuario y redirige al login."""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('usuarios:login')


# ──────────────────────────────────────────────
# Vista 3: Dashboard principal (panel de administración)
# ──────────────────────────────────────────────

@login_required
def vista_dashboard(request):
    """
    Panel principal tras iniciar sesión.
    Redirige a gestión de usuarios si tiene permisos.
    """
    return redirect('usuarios:gestion_usuarios')


# ──────────────────────────────────────────────
# Vista 4: Gestión de Usuarios
# ──────────────────────────────────────────────

@login_required
@requiere_jerarquia(nivel_minimo=50)
def vista_gestion_usuarios(request):
    """
    Subtarea 1.1: Panel de administración de usuarios y asignación de roles.
    Subtarea 1.3: Si el usuario no tiene permisos, se maneja con PermissionDenied (decorador).
    """
    usuarios = Usuario.objects.select_related('rol').all().order_by('username')
    roles = Rol.objects.all().order_by('-nivel_jerarquia')

    # Búsqueda/filtrado básico por nombre o email
    q = request.GET.get('q', '').strip()
    if q:
        usuarios = usuarios.filter(
            username__icontains=q
        ) | usuarios.filter(
            email__icontains=q
        ) | usuarios.filter(
            first_name__icontains=q
        )

    context = {
        'usuarios': usuarios,
        'roles': roles,
        'busqueda': q,
        'titulo': 'Gestión de Usuarios',
        'seccion_activa': 'gestion_usuarios',
    }
    return render(request, 'usuarios/gestion_usuarios.html', context)


# ──────────────────────────────────────────────
# Vista 5: Asignación de Rol (AJAX)
# ──────────────────────────────────────────────

@login_required
@requiere_jerarquia(nivel_minimo=100)
def vista_asignar_rol(request, usuario_id):
    """
    Subtarea 1.1: Asignación de roles desde el panel de administración.
    Acepta peticiones POST para cambiar el rol de un usuario.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    usuario_obj = get_object_or_404(Usuario, pk=usuario_id)
    rol_id = request.POST.get('rol_id')

    if rol_id:
        rol = get_object_or_404(Rol, pk=rol_id)
        usuario_obj.rol = rol
        usuario_obj.save(update_fields=['rol'])
        return JsonResponse({
            'success': True,
            'mensaje': f'Rol "{rol.nombre}" asignado correctamente a {usuario_obj.username}.',
            'rol_nombre': rol.nombre,
        })
    else:
        # Quitar rol
        usuario_obj.rol = None
        usuario_obj.save(update_fields=['rol'])
        return JsonResponse({
            'success': True,
            'mensaje': f'Rol removido del usuario {usuario_obj.username}.',
            'rol_nombre': 'Sin Rol',
        })


# ──────────────────────────────────────────────
# Vista 6: Página de Error 403 (sin permisos)
# ──────────────────────────────────────────────

def vista_sin_permisos(request, exception=None):
    """
    Subtarea 1.3: Página visual cuando el usuario no tiene permisos suficientes.
    """
    return render(request, 'usuarios/sin_permisos.html', {
        'titulo': 'Acceso Denegado',
        'mensaje': 'Tu rol no tiene los permisos suficientes para acceder a esta sección.',
    }, status=403)
