from functools import wraps

from django.core.exceptions import PermissionDenied


def requiere_jerarquia(nivel_minimo):
    """Decorador para vistas basadas en funciones con control jerárquico."""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Acceso denegado: Debes iniciar sesión.")

            if request.user.tiene_rango_minimo(nivel_minimo):
                return view_func(request, *args, **kwargs)

            raise PermissionDenied(
                "Acceso denegado: Tu rol no tiene los permisos suficientes para esta acción."
            )

        return _wrapped_view

    return decorator
