import time

from django.contrib import messages
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse

from configuracion.models import ConfiguracionGlobal
from usuarios.constants import MENSAJE_MANTENIMIENTO, NIVEL_ADMINISTRADOR

PREFIJOS_EXENTOS = (
    "/static/",
    "/media/",
    "/admin/",
)

MENSAJE_SESION_INACTIVA = "Tu sesión se cerró por inactividad. Inicia sesión de nuevo."
CLAVE_ULTIMA_ACTIVIDAD = "_ultima_actividad"


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._ruta_exenta(request.path):
            return self.get_response(request)

        try:
            config = ConfiguracionGlobal.obtener()
        except Exception:
            return self.get_response(request)

        if not config.modo_mantenimiento:
            return self.get_response(request)

        if self._es_administrador(request.user):
            return self.get_response(request)

        if request.user.is_authenticated:
            logout(request)

        if request.path.startswith("/api/"):
            return JsonResponse({"detail": MENSAJE_MANTENIMIENTO}, status=503)

        messages.warning(request, MENSAJE_MANTENIMIENTO)
        return redirect("usuarios:login")

    def _ruta_exenta(self, path):
        if any(path.startswith(prefijo) for prefijo in PREFIJOS_EXENTOS):
            return True
        try:
            rutas = {
                reverse("usuarios:login"),
                reverse("usuarios:login_alt"),
                reverse("usuarios:logout"),
                reverse("usuarios:password_reset"),
                reverse("usuarios:password_reset_done"),
                reverse("usuarios:password_reset_complete"),
            }
        except Exception:
            rutas = {"/", "/login/", "/logout/"}
        if path in rutas:
            return True
        if path.startswith("/password-reset-confirmar/"):
            return True
        return False

    def _es_administrador(self, user):
        if not getattr(user, "is_authenticated", False):
            return False
        if getattr(user, "is_superuser", False):
            return True
        if hasattr(user, "tiene_rango_minimo"):
            return user.tiene_rango_minimo(NIVEL_ADMINISTRADOR)
        rol = getattr(user, "rol", None)
        return bool(rol and rol.nivel_jerarquia >= NIVEL_ADMINISTRADOR)


class TiempoSesionMiddleware:
    """Aplica el "Tiempo de sesión" de Ajustes Globales como límite de INACTIVIDAD.

    - Si pasó más de ese tiempo desde la última petición, cierra la sesión.
    - Si no, renueva la marca de actividad y, cuando la sesión no es de las que
      terminan al cerrar el navegador, alinea su expiración en la base de datos
      (así "Control de Sesiones" muestra la fecha real).
    Debe ir después de AuthenticationMiddleware y MessageMiddleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        user = getattr(request, "user", None)

        if (
            user is None
            or not user.is_authenticated
            or path.startswith("/static/")
            or path.startswith("/media/")
        ):
            return self.get_response(request)

        try:
            minutos = int(ConfiguracionGlobal.obtener().tiempo_sesion_minutos or 0)
        except Exception:
            return self.get_response(request)

        if minutos <= 0:
            return self.get_response(request)

        segundos = minutos * 60
        ahora = int(time.time())
        ultima = request.session.get(CLAVE_ULTIMA_ACTIVIDAD)

        if ultima is not None and ahora - int(ultima) > segundos:
            logout(request)
            if path.startswith("/api/"):
                return JsonResponse({"detail": MENSAJE_SESION_INACTIVA}, status=401)
            messages.warning(request, MENSAJE_SESION_INACTIVA)
            return redirect("usuarios:login")

        request.session[CLAVE_ULTIMA_ACTIVIDAD] = ahora
        if not request.session.get_expire_at_browser_close():
            request.session.set_expiry(segundos)

        return self.get_response(request)