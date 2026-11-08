from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect

from usuarios.constants import MENSAJE_ACCESO_DENEGADO, MENSAJE_SESION_REEMPLAZADA
from usuarios.models import SecurityLog, Usuario
from usuarios.security import cuenta_bloqueada, registrar_evento

RUTAS_EXENTAS = {
    "/",
    "/login/",
    "/logout/",
    "/api/auth/login/",
    "/api/auth/login/refresh/",
    "/admin/login/",
}


class BloqueoCuentaMiddleware:
    """
    Verifica si la cuenta autenticada está bloqueada antes de procesar la petición.
    Debe ir después de AuthenticationMiddleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._debe_verificar(request) and cuenta_bloqueada(request.user):
            registrar_evento(
                request, SecurityLog.Accion.ACCESS_DENIED, user=request.user
            )
            logout(request)
            return self._respuesta_bloqueado(request)
        return self.get_response(request)

    def _debe_verificar(self, request):
        if not request.user.is_authenticated:
            return False
        path = request.path
        if path.startswith("/static/"):
            return False
        return path not in RUTAS_EXENTAS

    def _respuesta_bloqueado(self, request):
        if request.path.startswith("/api/"):
            return JsonResponse({"detail": MENSAJE_ACCESO_DENEGADO}, status=403)
        messages.error(request, MENSAJE_ACCESO_DENEGADO)
        return redirect("usuarios:login")


class SesionUnicaMiddleware:
    """Garantiza una sola sesión activa por usuario.

    - Si la sesión fue desplazada (otro login), `invalidar_sesion` la dejó
      anónima con la marca `sesion_reemplazada`: aquí se muestra el aviso.
    - Si por cualquier motivo una sesión antigua sigue autenticada pero su
      clave no coincide con la activa, se cierra igualmente.
    Debe ir después de AuthenticationMiddleware y antes de MessageMiddleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if path.startswith("/static/") or path.startswith("/media/"):
            return self.get_response(request)

        user = getattr(request, "user", None)
        es_api = path.startswith("/api/")

        # 1) Dispositivo desplazado: ya es anónimo, solo mostramos el aviso.
        if user is not None and not user.is_authenticated:
            if request.session.get("sesion_reemplazada"):
                request.session.pop("sesion_reemplazada", None)
                if es_api:
                    return JsonResponse(
                        {"detail": MENSAJE_SESION_REEMPLAZADA}, status=401
                    )
                messages.warning(request, MENSAJE_SESION_REEMPLAZADA)
            return self.get_response(request)

        # 2) Usuario autenticado: la clave de esta sesión debe ser la activa.
        if user is not None and user.is_authenticated:
            clave_actual = request.session.session_key
            clave_activa = getattr(user, "sesion_clave_activa", "") or ""

            if not clave_activa and clave_actual:
                Usuario.objects.filter(pk=user.pk).update(
                    sesion_clave_activa=clave_actual
                )
                user.sesion_clave_activa = clave_actual
            elif clave_activa and clave_actual and clave_actual != clave_activa:
                logout(request)
                if es_api:
                    return JsonResponse(
                        {"detail": MENSAJE_SESION_REEMPLAZADA}, status=401
                    )
                messages.warning(request, MENSAJE_SESION_REEMPLAZADA)
                return redirect("usuarios:login")

        return self.get_response(request)