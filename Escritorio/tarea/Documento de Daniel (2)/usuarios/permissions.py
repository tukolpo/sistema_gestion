from rest_framework import permissions  # type: ignore[import]

from usuarios.constants import NIVEL_GESTION_USUARIOS


class TieneJerarquiaMinima(permissions.BasePermission):
    """Permiso personalizado para Django REST Framework."""

    nivel_requerido = NIVEL_GESTION_USUARIOS

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        nivel = getattr(view, "nivel_requerido", self.nivel_requerido)
        return request.user.tiene_rango_minimo(nivel)
