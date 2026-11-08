from usuarios.constants import (
    NIVEL_ADMINISTRADOR,
    NIVEL_GESTION_USUARIOS,
    NIVEL_SUPERVISOR,
)


def permisos_globales(request):
    """Expone banderas de permiso usables en cualquier template (ej. base.html)."""
    autenticado = request.user.is_authenticated
    es_administrador = autenticado and request.user.tiene_rango_minimo(
        NIVEL_ADMINISTRADOR
    )
    puede_gestionar_usuarios = autenticado and request.user.tiene_rango_minimo(
        NIVEL_GESTION_USUARIOS
    )
    puede_supervisar = autenticado and request.user.tiene_rango_minimo(
        NIVEL_SUPERVISOR
    )
    return {
        "es_administrador": es_administrador,
        "puede_gestionar_usuarios": puede_gestionar_usuarios,
        "puede_supervisar": puede_supervisar,
    }