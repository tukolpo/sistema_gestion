from trabajadores_ext.auditoria import registrar
from trabajadores_ext.current_user import establecer_usuario_actual, limpiar_usuario_actual
from trabajadores_ext.models import AuditoriaTrabajador


class AuditoriaTrabajadorMiddleware:
    RUTAS = (
        "/trabajadores/",
        "/api/trabajadores/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Deja disponible el usuario de esta petición para las señales
        # (post_save/post_delete de Trabajador), que no reciben el request.
        usuario_autenticado = (
            request.user
            if getattr(request, "user", None) and request.user.is_authenticated
            else None
        )
        establecer_usuario_actual(usuario_autenticado)
        try:
            response = self.get_response(request)
        finally:
            limpiar_usuario_actual()

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