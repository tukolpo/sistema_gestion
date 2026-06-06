from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect

from usuarios.constants import MENSAJE_ACCESO_DENEGADO
from usuarios.models import SecurityLog
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


class AuditMiddleware:
    """
    Guarda el objeto request actual en thread locals para que 
    los signals de LogAuditoria puedan acceder al usuario y la IP.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from usuarios.signals import set_current_request
        set_current_request(request)
        response = self.get_response(request)
        set_current_request(None)
        return response
