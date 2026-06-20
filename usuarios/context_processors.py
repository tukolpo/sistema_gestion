from usuarios.constants import NIVEL_ADMINISTRADOR


def permisos_globales(request):
    """Expone banderas de permiso usables en cualquier template (ej. base.html)."""
    es_administrador = (
        request.user.is_authenticated
        and request.user.tiene_rango_minimo(NIVEL_ADMINISTRADOR)
    )
    return {"es_administrador": es_administrador}