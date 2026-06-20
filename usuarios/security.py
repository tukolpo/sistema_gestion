# usuarios/security.py
# Seguridad de sesión, bloqueos de cuenta y utilidades RBAC

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from usuarios.constants import MAX_INTENTOS_LOGIN, MINUTOS_BLOQUEO_LOGIN, NIVEL_ADMINISTRADOR
from usuarios.models import Rol, SecurityLog

User = get_user_model()


def obtener_ip(request):
    if request is None:
        return None
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def obtener_user_agent(request):
    if request is None:
        return ""
    return (request.META.get("HTTP_USER_AGENT") or "")[:512]


def registrar_evento(request, action, user=None):
    SecurityLog.objects.create(
        user=user,
        ip_address=obtener_ip(request),
        action=action,
        user_agent=obtener_user_agent(request),
    )


def cuenta_bloqueada(user):
    if user is None or not user.is_authenticated:
        return False
    return user.esta_bloqueado()


def _limpiar_bloqueo_expirado(user):
    if user.bloqueado_hasta and user.bloqueado_hasta <= timezone.now():
        user.intentos_fallidos_login = 0
        user.bloqueado_hasta = None
        user.save(update_fields=["intentos_fallidos_login", "bloqueado_hasta"])
        return False
    return user.esta_bloqueado()


def login_esta_bloqueado(user, request=None):
    if user is None:
        return False
    if _limpiar_bloqueo_expirado(user):
        registrar_evento(request, SecurityLog.Accion.LOGIN_FAILED, user=user)
        return True
    return False


def registrar_login_fallido(request, user=None):
    if user is not None:
        user.intentos_fallidos_login += 1
        update_fields = ["intentos_fallidos_login"]
        if user.intentos_fallidos_login >= MAX_INTENTOS_LOGIN:
            user.bloqueado_hasta = timezone.now() + timedelta(
                minutes=MINUTOS_BLOQUEO_LOGIN
            )
            update_fields.append("bloqueado_hasta")
        user.save(update_fields=update_fields)
    registrar_evento(request, SecurityLog.Accion.LOGIN_FAILED, user=user)


def registrar_login_exitoso(request, user):
    if user.intentos_fallidos_login or user.bloqueado_hasta:
        user.intentos_fallidos_login = 0
        user.bloqueado_hasta = None
        user.save(update_fields=["intentos_fallidos_login", "bloqueado_hasta"])
    registrar_evento(request, SecurityLog.Accion.LOGIN_SUCCESS, user=user)


def buscar_usuario_por_email(email):
    if not email:
        return None
    return User.objects.filter(email__iexact=email.strip()).first()


def nivel_usuario(user):
    if user.is_superuser:
        return NIVEL_ADMINISTRADOR
    return user.rol.nivel_jerarquia if user.rol else 0


def roles_asignables(user):
    if user.is_superuser:
        return Rol.objects.all().order_by("-nivel_jerarquia")
    max_nivel = nivel_usuario(user)
    return Rol.objects.filter(nivel_jerarquia__lte=max_nivel).order_by(
        "-nivel_jerarquia"
    )
