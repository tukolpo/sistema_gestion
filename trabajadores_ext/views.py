from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from usuarios.constants import NIVEL_ADMINISTRADOR, NIVEL_GESTION_USUARIOS
from usuarios.decorators import requiere_jerarquia

from trabajadores.models import Trabajador
from trabajadores_ext.auditoria import registrar
from trabajadores_ext.models import AuditoriaTrabajador, EscaneoQR, TrabajadorTokenQR
from trabajadores_ext.qr import generar_imagen_qr, obtener_token_qr, url_perfil_publico


def _ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_GESTION_USUARIOS)
def vista_credencial_qr(request, trabajador_id):
    trabajador = get_object_or_404(
        Trabajador.objects.select_related("cargo", "especialidad"),
        pk=trabajador_id,
    )
    token_obj = obtener_token_qr(trabajador)
    url_publica = url_perfil_publico(request, token_obj.token)
    registrar(
        AuditoriaTrabajador.Accion.QR_GENERADO,
        request=request,
        trabajador=trabajador,
        tabla="trabajadores_ext_trabajadortokenqr",
        registro_id=token_obj.pk,
        valor_nuevo=str(token_obj.token),
    )
    return render(
        request,
        "trabajadores_ext/credencial_qr.html",
        {
            "trabajador": trabajador,
            "url_publica": url_publica,
            "token": token_obj.token,
            "titulo": f"Credencial QR — {trabajador}",
            "seccion_activa": "trabajadores",
        },
    )


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_GESTION_USUARIOS)
def vista_qr_imagen(request, trabajador_id):
    trabajador = get_object_or_404(Trabajador, pk=trabajador_id)
    token_obj = obtener_token_qr(trabajador)
    if not token_obj.activo:
        raise Http404()
    url_publica = url_perfil_publico(request, token_obj.token)
    buffer = generar_imagen_qr(url_publica)
    return HttpResponse(buffer.getvalue(), content_type="image/png")


def vista_perfil_publico(request, token):
    token_obj = get_object_or_404(
        TrabajadorTokenQR.objects.select_related(
            "trabajador", "trabajador__cargo", "trabajador__especialidad"
        ),
        token=token,
        activo=True,
    )
    trabajador = token_obj.trabajador
    if not trabajador.esta_activo:
        raise Http404()
    EscaneoQR.objects.create(
        token_qr=token_obj,
        ip=_ip(request),
        user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:512],
    )
    registrar(
        AuditoriaTrabajador.Accion.QR_ESCANEADO,
        request=request,
        trabajador=trabajador,
        tabla="trabajadores_ext_trabajadortokenqr",
        registro_id=token_obj.pk,
    )
    return render(
        request,
        "trabajadores_ext/perfil_publico.html",
        {
            "trabajador": trabajador,
            "token": token,
            "titulo": "Verificación de identidad",
        },
    )


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_ADMINISTRADOR)
def vista_auditoria(request):
    registros = AuditoriaTrabajador.objects.select_related("trabajador", "usuario")
    q = request.GET.get("q", "").strip()
    accion = request.GET.get("accion", "").strip()
    if q:
        registros = registros.filter(
            Q(trabajador__nombre__icontains=q)
            | Q(trabajador__apellido__icontains=q)
            | Q(trabajador__cedula__icontains=q)
            | Q(usuario__username__icontains=q)
        )
    if accion in AuditoriaTrabajador.Accion.values:
        registros = registros.filter(accion=accion)
    return render(
        request,
        "trabajadores_ext/auditoria.html",
        {
            "registros": registros[:500],
            "busqueda": q,
            "filtro_accion": accion,
            "acciones": AuditoriaTrabajador.Accion.choices,
            "titulo": "Auditoría de trabajadores",
            "seccion_activa": "auditoria",
        },
    )