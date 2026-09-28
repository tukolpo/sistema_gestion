from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

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


# ─── Metadatos visuales por tipo de acción (icono + color) ───────────
_ICONOS_ACCION = {
    AuditoriaTrabajador.Accion.CREAR: ("fa-circle-plus", "#2b6b3a", "#e6f7ec"),
    AuditoriaTrabajador.Accion.ACTUALIZAR: ("fa-pen", "#2E5C8A", "#e8f0fe"),
    AuditoriaTrabajador.Accion.ELIMINAR: ("fa-trash", "#8b1a2b", "#fdeceb"),
    AuditoriaTrabajador.Accion.ESTADO: ("fa-toggle-on", "#8a5a00", "#fff6e0"),
    AuditoriaTrabajador.Accion.DOCUMENTO: ("fa-file-lines", "#5b3fa0", "#f1ecfb"),
    AuditoriaTrabajador.Accion.QR_GENERADO: ("fa-qrcode", "#2E5C8A", "#e8f0fe"),
    AuditoriaTrabajador.Accion.QR_ESCANEADO: ("fa-camera", "#2E5C8A", "#e8f0fe"),
    AuditoriaTrabajador.Accion.ACCESO: ("fa-eye", "#64748b", "#eef2f7"),
}
_ICONO_DEFECTO = ("fa-circle-info", "#64748b", "#eef2f7")

# Ventana de agrupación: entradas del MISMO usuario+acción+detalle consecutivas
# en la lista (ya ordenada por fecha desc) se colapsan en una sola tarjeta.
_LIMITE_REGISTROS = 1000


def _agrupar_consecutivos(registros):
    """Colapsa filas consecutivas idénticas (mismo usuario, acción y detalle)
    en un solo grupo con contador, para reducir el ruido de accesos repetidos."""
    grupos = []
    actual = None

    for r in registros:
        detalle = r.valor_nuevo or r.ruta
        clave = (r.usuario_id, r.accion, r.trabajador_id, detalle)

        if actual and actual["clave"] == clave:
            actual["cantidad"] += 1
            actual["desde"] = r.creado_en  # vamos retrocediendo en el tiempo
        else:
            icono, color, fondo = _ICONOS_ACCION.get(r.accion, _ICONO_DEFECTO)
            # Para "Actualizar" el detalle viene como "Campo: antes → después; Campo2: ...".
            # Lo separamos para mostrarlo como una lista legible, no una frase larga.
            cambios = []
            if r.accion == AuditoriaTrabajador.Accion.ACTUALIZAR and r.valor_nuevo:
                cambios = [c.strip() for c in r.valor_nuevo.split(";") if c.strip()]
            actual = {
                "clave": clave,
                "registro": r,
                "cantidad": 1,
                "hasta": r.creado_en,
                "desde": r.creado_en,
                "icono": icono,
                "color": color,
                "fondo": fondo,
                "cambios": cambios,
            }
            grupos.append(actual)

    return grupos


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_ADMINISTRADOR)
def vista_auditoria(request):
    base_qs = AuditoriaTrabajador.objects.select_related("trabajador", "usuario")

    q = request.GET.get("q", "").strip()
    accion = request.GET.get("accion", "").strip()

    registros_qs = base_qs
    if q:
        registros_qs = registros_qs.filter(
            Q(trabajador__nombre__icontains=q)
            | Q(trabajador__apellido__icontains=q)
            | Q(trabajador__cedula__icontains=q)
            | Q(usuario__username__icontains=q)
        )
    if accion in AuditoriaTrabajador.Accion.values:
        registros_qs = registros_qs.filter(accion=accion)

    # ── Estadísticas (sobre el total filtrado, no sobre la página actual) ──
    hoy = timezone.localdate()
    total_eventos = registros_qs.count()
    accesos_hoy = registros_qs.filter(
        accion=AuditoriaTrabajador.Accion.ACCESO, creado_en__date=hoy
    ).count()
    cambios_hoy = registros_qs.filter(creado_en__date=hoy).exclude(
        accion=AuditoriaTrabajador.Accion.ACCESO
    ).count()
    eliminaciones_totales = registros_qs.filter(
        accion=AuditoriaTrabajador.Accion.ELIMINAR
    ).count()

    # ── Agrupar consecutivos y paginar el resultado agrupado ──
    registros = list(registros_qs[:_LIMITE_REGISTROS])
    grupos = _agrupar_consecutivos(registros)

    paginator = Paginator(grupos, 25)
    numero_pagina = request.GET.get("page")
    pagina = paginator.get_page(numero_pagina)

    # ── Agrupar la página actual por día para la vista tipo timeline ──
    dias = []
    dia_actual = None
    for item in pagina.object_list:
        fecha_local = timezone.localtime(item["hasta"]).date()
        if dia_actual is None or dia_actual["fecha"] != fecha_local:
            dia_actual = {"fecha": fecha_local, "items": []}
            dias.append(dia_actual)
        dia_actual["items"].append(item)

    return render(
        request,
        "trabajadores_ext/auditoria.html",
        {
            "dias": dias,
            "pagina": pagina,
            "busqueda": q,
            "filtro_accion": accion,
            "acciones": AuditoriaTrabajador.Accion.choices,
            "titulo": "Auditoría de trabajadores",
            "seccion_activa": "auditoria",
            "total_eventos": total_eventos,
            "accesos_hoy": accesos_hoy,
            "cambios_hoy": cambios_hoy,
            "eliminaciones_totales": eliminaciones_totales,
        },
    )