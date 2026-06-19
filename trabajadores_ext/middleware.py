from trabajadores_ext.auditoria import registrar
from trabajadores_ext.models import AuditoriaTrabajador


class AuditoriaTrabajadorMiddleware:
    RUTAS = (
        "/trabajadores/",
        "/api/trabajadores/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            return response
        if not request.user.is_authenticated:
            return response
        path = request.path
        if not any(path.startswith(p) for p in self.RUTAS):
            return response
        if path.endswith(("/foto/", "/qr/", "/qr/imagen/")):
            return response
        registrar(
            AuditoriaTrabajador.Accion.ACCESO,
            request=request,
            tabla="http",
            valor_nuevo=path,
        )
        return response
