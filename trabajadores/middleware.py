"""
Middleware de acceso restringido a archivos (3.4).
Bloquea cualquier intento de acceder a rutas de medios privados sin pasar por las vistas protegidas.
"""

from django.http import HttpResponseForbidden


class ArchivoPrivadoMiddleware:
    RUTAS_BLOQUEADAS = (
        "/private-media/",
        "/private_media/",
        "/media/trabajadores/",
        "/media/private/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.lower()
        for bloqueada in self.RUTAS_BLOQUEADAS:
            if path.startswith(bloqueada):
                return HttpResponseForbidden(
                    "Acceso directo a archivos no permitido."
                )
        return self.get_response(request)
