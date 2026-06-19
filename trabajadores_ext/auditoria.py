from trabajadores_ext.models import AuditoriaTrabajador


def _ip(request):
    if request is None:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _ua(request):
    if request is None:
        return ""
    return (request.META.get("HTTP_USER_AGENT") or "")[:512]


def registrar(
    accion,
    request=None,
    trabajador=None,
    tabla="",
    registro_id=None,
    valor_anterior="",
    valor_nuevo="",
    usuario=None,
):
    user = usuario
    if user is None and request is not None and getattr(request, "user", None):
        if request.user.is_authenticated:
            user = request.user
    return AuditoriaTrabajador.objects.create(
        trabajador=trabajador,
        usuario=user,
        accion=accion,
        tabla=tabla or "",
        registro_id=registro_id,
        valor_anterior=str(valor_anterior)[:4000],
        valor_nuevo=str(valor_nuevo)[:4000],
        ip=_ip(request),
        user_agent=_ua(request),
        ruta=getattr(request, "path", "") if request else "",
    )
