# usuarios/views.py
# Integrante 1: Vistas web (login, panel, gestión de usuarios, roles)

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
from usuarios.forms import LoginForm, UsuarioCreationForm, UsuarioChangeForm, CambiarPasswordForm, RolForm
from usuarios.models import Rol, Usuario, LogAuditoria
from usuarios.security import (
    nivel_usuario,
    registrar_login_exitoso,
    roles_asignables,
)


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


# ──────────────────────────────────────────────────────────────────────────────
# GESTIÓN DE USUARIOS
# ──────────────────────────────────────────────────────────────────────────────

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


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_GESTION_USUARIOS)
def crear_usuario(request):
    if request.method == "POST":
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f"Usuario '{usuario.username}' creado correctamente.")
            return redirect("usuarios:gestion_usuarios")
    else:
        form = UsuarioCreationForm()

    return render(
        request,
        "usuarios/formulario_usuario.html",
        {"form": form, "titulo": "Crear Nuevo Usuario", "seccion_activa": "gestion_usuarios"}
    )


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_GESTION_USUARIOS)
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == "POST":
        form = UsuarioChangeForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f"Usuario '{usuario.username}' actualizado correctamente.")
            return redirect("usuarios:gestion_usuarios")
    else:
        form = UsuarioChangeForm(instance=usuario)

    return render(
        request,
        "usuarios/formulario_usuario.html",
        {"form": form, "titulo": f"Editar: {usuario.username}", "seccion_activa": "gestion_usuarios"}
    )


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_GESTION_USUARIOS)
def cambiar_password(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == "POST":
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            usuario.set_password(form.cleaned_data["password1"])
            usuario.save()
            messages.success(request, f"Contraseña de '{usuario.username}' cambiada correctamente.")
            return redirect("usuarios:gestion_usuarios")
    else:
        form = CambiarPasswordForm()

    return render(
        request,
        "usuarios/formulario_password.html",
        {"form": form, "usuario_obj": usuario, "titulo": f"Cambiar Contraseña: {usuario.username}", "seccion_activa": "gestion_usuarios"}
    )


# ──────────────────────────────────────────────────────────────────────────────
# AUDITORÍA
# ──────────────────────────────────────────────────────────────────────────────

@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_GESTION_USUARIOS)
def vista_auditoria(request):
    logs = LogAuditoria.objects.select_related("usuario").all().order_by("-fecha")[:200]
    return render(
        request,
        "usuarios/auditoria.html",
        {"logs": logs, "titulo": "Registro de Auditoría", "seccion_activa": "auditoria"}
    )


# ──────────────────────────────────────────────────────────────────────────────
# CRUD DE ROLES Y PERMISOS
# ──────────────────────────────────────────────────────────────────────────────

@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_GESTION_USUARIOS)
def lista_roles(request):
    roles = Rol.objects.all().order_by("-nivel_jerarquia")
    return render(
        request,
        "usuarios/lista_roles.html",
        {"roles": roles, "titulo": "Roles y Permisos", "seccion_activa": "roles"}
    )


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_GESTION_USUARIOS)
def crear_rol(request):
    if request.method == "POST":
        form = RolForm(request.POST)
        if form.is_valid():
            rol = form.save()
            messages.success(request, f"Rol '{rol.nombre}' creado correctamente.")
            return redirect("usuarios:lista_roles")
    else:
        form = RolForm()

    return render(
        request,
        "usuarios/formulario_rol.html",
        {"form": form, "titulo": "Crear Nuevo Rol", "seccion_activa": "roles"}
    )


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_GESTION_USUARIOS)
def editar_rol(request, rol_id):
    rol = get_object_or_404(Rol, pk=rol_id)
    if request.method == "POST":
        form = RolForm(request.POST, instance=rol)
        if form.is_valid():
            form.save()
            messages.success(request, f"Rol '{rol.nombre}' actualizado correctamente.")
            return redirect("usuarios:lista_roles")
    else:
        form = RolForm(instance=rol)

    return render(
        request,
        "usuarios/formulario_rol.html",
        {"form": form, "titulo": f"Editar Rol: {rol.nombre}", "seccion_activa": "roles"}
    )


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_GESTION_USUARIOS)
def eliminar_rol(request, rol_id):
    rol = get_object_or_404(Rol, pk=rol_id)
    if request.method == "POST":
        nombre = rol.nombre
        rol.delete()
        messages.success(request, f"Rol '{nombre}' eliminado correctamente.")
    return redirect("usuarios:lista_roles")
