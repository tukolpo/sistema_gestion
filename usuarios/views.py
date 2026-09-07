

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count
from trabajadores.models import Trabajador
from vacaciones.models import SolicitudVacaciones

from usuarios.constants import (
    NIVEL_ASIGNAR_ROLES,
    NIVEL_GESTION_USUARIOS,
    NIVEL_DASHBOARD_GENERAL,
)
from usuarios.decorators import requiere_jerarquia
from usuarios.forms import LoginForm, CrearUsuarioForm
from usuarios.models import Rol, Usuario
from usuarios.security import (
    nivel_usuario,
    registrar_login_exitoso,
    roles_asignables,
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
    puede_ver_dashboard_general = request.user.tiene_rango_minimo(NIVEL_DASHBOARD_GENERAL)

    contexto = {
        "titulo": "Inicio",
        "seccion_activa": "inicio",
        "puede_ver_dashboard_general": puede_ver_dashboard_general,
    }

    if puede_ver_dashboard_general:
        total_trabajadores = Trabajador.objects.count()
        activos = Trabajador.objects.filter(estado=Trabajador.Estado.ACTIVO).count()

        contexto.update({
            "total_trabajadores": total_trabajadores,
            "activos": activos,
            "inactivos": total_trabajadores - activos,
            "personal_por_cargo": Trabajador.objects.values("cargo__nombre")
                .annotate(total=Count("id")).order_by("-total"),
            "vacaciones_pendientes": SolicitudVacaciones.objects.filter(
                estado=SolicitudVacaciones.Estado.PENDIENTE
            ).count(),
        })

    return render(request, "usuarios/inicio.html", contexto)


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
def vista_crear_usuario(request):
    if request.method == "POST":
        form = CrearUsuarioForm(
            request.POST,
            roles_disponibles=roles_asignables(request.user),
            admin_user=request.user,
        )
        if form.is_valid():
            usuario = form.guardar()
            messages.success(request, f"Usuario {usuario.email} creado correctamente.")
            return redirect("usuarios:gestion_usuarios")
    else:
        form = CrearUsuarioForm(
            roles_disponibles=roles_asignables(request.user),
            admin_user=request.user,
        )

    return render(request, "usuarios/crear_usuario.html", {
        "form": form,
        "titulo": "Nuevo Usuario",
        "seccion_activa": "gestion_usuarios",
    })

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
