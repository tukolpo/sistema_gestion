# usuarios/permissions.py
from rest_framework import permissions  # type: ignore[import]

class TieneJerarquiaMinima(permissions.BasePermission):
    """
    Permiso personalizado para Django REST Framework.
    """
    nivel_requerido = 50 # Valor por defecto, se puede sobrescribir en la vista

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Leemos si la vista definió un nivel específico requerido
        nivel = getattr(view, 'nivel_requerido', self.nivel_requerido)
        return request.user.tiene_rango_minimo(nivel)