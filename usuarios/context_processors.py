from usuarios.constants import NIVEL_ADMINISTRADOR, NIVEL_GESTION_USUARIOS


def permisos_globales(request):
    """Expone banderas de permiso usables en cualquier template (ej. base.html)."""
    es_administrador = (
        request.user.is_authenticated
        and request.user.tiene_rango_minimo(NIVEL_ADMINISTRADOR)
    )
    puede_gestionar_usuarios = (
        request.user.is_authenticated
        and request.user.tiene_rango_minimo(NIVEL_GESTION_USUARIOS)
    )
    return {
        "es_administrador": es_administrador,
        "puede_gestionar_usuarios": puede_gestionar_usuarios,
    }