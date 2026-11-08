# usuarios/security.py
# Seguridad de sesión, bloqueos de cuenta y utilidades RBAC

from datetime import timedelta
from importlib import import_module

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from usuarios.constants import MAX_INTENTOS_LOGIN, MINUTOS_BLOQUEO_LOGIN, NIVEL_ADMINISTRADOR
from usuarios.models import Rol, SecurityLog

User = get_user_model()

CLAVES_AUTH_SESION = ("_auth_user_id", "_auth_user_backend", "_auth_user_hash")

# Roles que no se ofrecen en los desplegables de asignación (por nombre).
# Para volver a mostrar uno, quítalo de esta lista.
ROLES_NO_ASIGNABLES = ("Trabajador",)


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


def limites_login():
    """Intentos máximos y minutos de bloqueo según Ajustes Globales.

    Si la configuración no está disponible, se usan las constantes por defecto.
    """
    try:
        from configuracion.models import ConfiguracionGlobal

        config = ConfiguracionGlobal.obtener()
        intentos = int(config.max_intentos_login or 0) or MAX_INTENTOS_LOGIN
        minutos = int(config.minutos_bloqueo_login or 0) or MINUTOS_BLOQUEO_LOGIN
        return intentos, minutos
    except Exception:
        return MAX_INTENTOS_LOGIN, MINUTOS_BLOQUEO_LOGIN


def registrar_login_fallido(request, user=None):
    if user is not None:
        max_intentos, minutos_bloqueo = limites_login()
        user.intentos_fallidos_login += 1
        update_fields = ["intentos_fallidos_login"]
        if user.intentos_fallidos_login >= max_intentos:
            user.bloqueado_hasta = timezone.now() + timedelta(
                minutes=minutos_bloqueo
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


# ─────────────────────────────────────────────────────────────
# Sesión única por usuario
# ─────────────────────────────────────────────────────────────

def invalidar_sesion(clave):
    """Cierra una sesión concreta (por su clave) sin borrarla.

    Se le quitan las credenciales de autenticación y se marca con
    `sesion_reemplazada`, de modo que el dispositivo desplazado quede
    como anónimo y, en su siguiente petición, vea el aviso.
    Es una operación O(1): no recorre la tabla de sesiones.
    """
    if not clave:
        return
    SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
    store = SessionStore(session_key=clave)
    if not store.exists(clave):
        return
    for k in CLAVES_AUTH_SESION:
        store.pop(k, None)
    store["sesion_reemplazada"] = True
    store.save()


def establecer_sesion_unica(request, user):
    """Deja una sola sesión activa para el usuario.

    La sesión actual pasa a ser la activa; la anterior (si existe) se
    invalida. Es idempotente: llamarla dos veces seguidas no hace nada
    la segunda vez.
    """
    if request is None or user is None:
        return
    if not request.session.session_key:
        request.session.save()

    clave_actual = request.session.session_key
    # Se lee de la BD (no de la instancia) para evitar valores obsoletos.
    anterior = (
        User.objects.filter(pk=user.pk)
        .values_list("sesion_clave_activa", flat=True)
        .first()
        or ""
    )

    if anterior == clave_actual:
        user.sesion_clave_activa = clave_actual
        return

    if anterior:
        invalidar_sesion(anterior)

    User.objects.filter(pk=user.pk).update(sesion_clave_activa=clave_actual)
    user.sesion_clave_activa = clave_actual


def liberar_sesion_activa(request, user):
    """Limpia la clave activa solo si pertenece a la sesión que se cierra."""
    if request is None or user is None or not getattr(user, "pk", None):
        return
    clave = request.session.session_key
    if not clave:
        return
    User.objects.filter(pk=user.pk, sesion_clave_activa=clave).update(
        sesion_clave_activa=""
    )


def buscar_usuario_por_email(email):
    if not email:
        return None
    return User.objects.filter(email__iexact=email.strip()).first()


def nivel_usuario(user):
    if user.is_superuser:
        return NIVEL_ADMINISTRADOR
    return user.rol.nivel_jerarquia if user.rol else 0


def roles_asignables(user):
    """Roles que se pueden asignar desde la interfaz.

    El rol de Administrador nunca aparece aquí para nadie, ni siquiera
    para un superusuario de Django: ese cambio solo puede hacerse
    directamente en la base de datos o el admin de Django.
    """
    base = Rol.objects.exclude(nivel_jerarquia__gte=NIVEL_ADMINISTRADOR)
    for nombre in ROLES_NO_ASIGNABLES:
        base = base.exclude(nombre__iexact=nombre)

    if user.is_superuser:
        return base.order_by("-nivel_jerarquia")

    max_nivel = nivel_usuario(user)
    return base.filter(nivel_jerarquia__lte=max_nivel).order_by("-nivel_jerarquia")