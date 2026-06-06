# usuarios/views.py
# Integrante 1: Vistas web (login, panel, gestión de usuarios)

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.constants import (
    NIVEL_ASIGNAR_ROLES,
    NIVEL_GESTION_USUARIOS,
)
from usuarios.decorators import requiere_jerarquia
from usuarios.forms import LoginForm
from usuarios.models import Rol, Usuario
from usuarios.security import (
    nivel_usuario,
    registrar_login_exitoso,
    roles_asignables,
)

from .forms import LoginForm
from usuarios.security import registrar_login_exitoso


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


def vista_login(request):
    if request.user.is_authenticated:
        return redirect("usuarios:dashboard")

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        registrar_login_exitoso(request, user)

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


@login_required
def vista_logout(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("usuarios:login")


@login_required
def vista_dashboard(request):
    if request.user.tiene_rango_minimo(NIVEL_GESTION_USUARIOS):
        return redirect("usuarios:gestion_usuarios")

    return render(
        request,
        "usuarios/inicio.html",
        {"titulo": "Inicio", "seccion_activa": "inicio"},
    )


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


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_GESTION_USUARIOS)
def vista_gestion_usuarios(request):
    usuarios = Usuario.objects.select_related("rol").all().order_by("username")
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
            "roles": roles_asignables(request.user),
            "busqueda": q,
            "titulo": "Gestión de Usuarios",
            "seccion_activa": "gestion_usuarios",
            "puede_asignar_roles": request.user.tiene_rango_minimo(
                NIVEL_ASIGNAR_ROLES
            ),
        },
    )


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_ASIGNAR_ROLES)
def vista_asignar_rol(request, usuario_id):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    usuario_obj = get_object_or_404(Usuario, pk=usuario_id)
    rol_id = request.POST.get("rol_id")

    if rol_id:
        rol = get_object_or_404(Rol, pk=rol_id)
        if not request.user.is_superuser and rol.nivel_jerarquia > nivel_usuario(
            request.user
        ):
            return JsonResponse(
                {"error": "No puedes asignar un rol superior al tuyo."},
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
