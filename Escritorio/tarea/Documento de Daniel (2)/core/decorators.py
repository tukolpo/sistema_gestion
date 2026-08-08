# usuarios/decorators.py
from django.core.exceptions import PermissionDenied
from functools import wraps

def requiere_jerarquia(nivel_minimo):
    """
    Decorador para vistas basadas en funciones.
    Filtra si el usuario logueado tiene el rango necesario.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 1. Verificar que el usuario exista y esté autenticado
            if not request.user.is_authenticated:
                raise PermissionDenied("Acceso denegado: Debes iniciar sesión.")
            
            # 2. Verificar jerarquía
            if request.user.tiene_rango_minimo(nivel_minimo):
                return view_func(request, *args, **kwargs)
            
            # 3. Bloqueo si no cumple el rol
            raise PermissionDenied("Acceso denegado: Tu rol no tiene los permisos suficientes para esta acción.")
        return _wrapped_view
    return decorator