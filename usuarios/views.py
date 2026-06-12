# usuarios/views.py
# Integrante 1: Subtareas 1.1, 1.2, 1.3
# Vistas para Login, Logout y Gestión de Usuarios con manejo de errores visuales.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

from usuarios.models import Usuario, Rol
from usuarios.decorators import requiere_jerarquia
from usuarios.constants import (
    NIVEL_GESTION_USUARIOS,
    NIVEL_ASIGNAR_ROLES,
)
from .forms import LoginForm


def _nivel_usuario(user):
    if user.is_superuser:
        return 100
    return user.rol.nivel_jerarquia if user.rol else 0


def _roles_asignables(user):
    if user.is_superuser:
        return Rol.objects.all().order_by("-nivel_jerarquia")
    max_nivel = _nivel_usuario(user)
    return Rol.objects.filter(nivel_jerarquia__lte=max_nivel).order_by(
        "-nivel_jerarquia"
    )


# ──────────────────────────────────────────────
# Vista 1: Login
# ──────────────────────────────────────────────


def vista_login(request):
    """
    Subtarea 1.1 & 1.3:
    Muestra el formulario de inicio de sesión y maneja errores visuales.
    """
    if request.user.is_authenticated:
        return redirect("usuarios:dashboard")

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)

        if not form.cleaned_data.get("remember_me"):
            request.session.set_expiry(0)

        messages.success(
            request, f"¡Bienvenido, {user.first_name or user.username}!"
        )
        return redirect("usuarios:dashboard")

    return render(
        request,
        "usuarios/login.html",
        {"form": form, "titulo": "Iniciar Sesión"},
    )


# ──────────────────────────────────────────────
# Vista 2: Logout
# ──────────────────────────────────────────────


@login_required
def vista_logout(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("usuarios:login")


# ──────────────────────────────────────────────
# Vista 3: Dashboard principal
# ──────────────────────────────────────────────


@login_required
def vista_dashboard(request):
    if request.user.tiene_rango_minimo(NIVEL_GESTION_USUARIOS):
        return redirect("usuarios:gestion_usuarios")

    return render(
        request,
        "usuarios/inicio.html",
        {
            "titulo": "Inicio",
            "seccion_activa": "inicio",
        },
    )


# ──────────────────────────────────────────────
# Vista 4: Gestión de Usuarios
# ──────────────────────────────────────────────


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_GESTION_USUARIOS)
def vista_gestion_usuarios(request):
    usuarios = Usuario.objects.select_related("rol").all().order_by("username")
    roles = _roles_asignables(request.user)

    q = request.GET.get("q", "").strip()
    if q:
        usuarios = usuarios.filter(
            Q(username__icontains=q)
            | Q(email__icontains=q)
            | Q(first_name__icontains=q)
        )

    return render(
        request,
        "usuarios/gestion_usuarios.html",
        {
            "usuarios": usuarios,
            "roles": roles,
            "busqueda": q,
            "titulo": "Gestión de Usuarios",
            "seccion_activa": "gestion_usuarios",
            "puede_asignar_roles": request.user.tiene_rango_minimo(
                NIVEL_ASIGNAR_ROLES
            ),
        },
    )


# ──────────────────────────────────────────────
# Vista 5: Asignación de Rol (AJAX)
# ──────────────────────────────────────────────


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_ASIGNAR_ROLES)
def vista_asignar_rol(request, usuario_id):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    usuario_obj = get_object_or_404(Usuario, pk=usuario_id)
    rol_id = request.POST.get("rol_id")

    if rol_id:
        rol = get_object_or_404(Rol, pk=rol_id)
        if not request.user.is_superuser and rol.nivel_jerarquia > _nivel_usuario(
            request.user
        ):
            return JsonResponse(
                {
                    "error": "No puedes asignar un rol superior al tuyo.",
                },
                status=403,
            )
        usuario_obj.rol = rol
        usuario_obj.save(update_fields=["rol"])
        return JsonResponse(
            {
                "success": True,
                "mensaje": (
                    f'Rol "{rol.nombre}" asignado correctamente a '
                    f"{usuario_obj.username}."
                ),
                "rol_nombre": rol.nombre,
            }
        )

    usuario_obj.rol = None
    usuario_obj.save(update_fields=["rol"])
    return JsonResponse(
        {
            "success": True,
            "mensaje": f"Rol removido del usuario {usuario_obj.username}.",
            "rol_nombre": "Sin Rol",
        }
    )


# ──────────────────────────────────────────────
# Vista 6: Página de Error 403 (sin permisos)
# ──────────────────────────────────────────────


def vista_sin_permisos(request, exception=None):
    return render(
        request,
        "usuarios/sin_permisos.html",
        {
            "titulo": "Acceso Denegado",
            "mensaje": (
                "Tu rol no tiene los permisos suficientes "
                "para acceder a esta sección."
            ),
        },
        status=403,
    )
