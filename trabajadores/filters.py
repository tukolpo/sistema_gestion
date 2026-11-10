# trabajadores/filters.py
# Motor de filtrado inteligente: lo usan la API (lista) y la exportación.

from datetime import date

from django.db.models import F, Q
from django.utils import timezone
from django.utils.dateparse import parse_date

from trabajadores.models import DocumentoTrabajador, Trabajador

ORDENES = {
    "nombre": ("apellido", "nombre"),
    "nombre_desc": ("-apellido", "-nombre"),
    "cedula": ("cedula",),
    "ingreso_antiguo": (F("fecha_ingreso").asc(nulls_last=True), "apellido"),
    "ingreso_reciente": (F("fecha_ingreso").desc(nulls_last=True), "apellido"),
}


def _fecha_limite_antiguedad(anios: int) -> date:
    hoy = timezone.now().date()
    try:
        return hoy.replace(year=hoy.year - anios)
    except ValueError:
        return hoy.replace(year=hoy.year - anios, day=28)


def aplicar_filtros_trabajadores(queryset, params):
    """
    Filtros opcionales y combinables sobre un queryset de Trabajador.
    Parametros: q, estatus (o estado), antiguedad (minima, en anios),
    antiguedad_max, ingreso_desde, ingreso_hasta, documentos (con|sin), orden.
    """
    filtros = Q()

    # Texto: cada palabra debe aparecer en nombre, apellido o cedula.
    q = (params.get("q") or "").strip()
    for palabra in q.split():
        filtros &= (
            Q(nombre__icontains=palabra)
            | Q(apellido__icontains=palabra)
            | Q(cedula__icontains=palabra)
        )

    departamento = (params.get("departamento") or "").strip()
    if departamento:
        filtros &= Q(departamento__icontains=departamento)

    estatus = (params.get("estatus") or params.get("estado") or "").strip()
    if estatus in Trabajador.Estado.values:
        filtros &= Q(estado=estatus)

    antiguedad = (params.get("antiguedad") or "").strip()
    if antiguedad.isdigit():
        filtros &= Q(
            fecha_ingreso__isnull=False,
            fecha_ingreso__lte=_fecha_limite_antiguedad(int(antiguedad)),
        )

    antiguedad_max = (params.get("antiguedad_max") or "").strip()
    if antiguedad_max.isdigit():
        # "hasta N anios cumplidos": ingreso posterior a hoy - (N+1) anios.
        filtros &= Q(
            fecha_ingreso__isnull=False,
            fecha_ingreso__gt=_fecha_limite_antiguedad(int(antiguedad_max) + 1),
        )

    desde = parse_date((params.get("ingreso_desde") or "").strip() or "x")
    if desde:
        filtros &= Q(fecha_ingreso__gte=desde)
    hasta = parse_date((params.get("ingreso_hasta") or "").strip() or "x")
    if hasta:
        filtros &= Q(fecha_ingreso__lte=hasta)

    documentos = (params.get("documentos") or "").strip()
    con_docs = Q(pk__in=DocumentoTrabajador.objects.values("trabajador_id"))
    if documentos == "con":
        filtros &= con_docs
    elif documentos == "sin":
        filtros &= ~con_docs

    if filtros:
        queryset = queryset.filter(filtros)

    orden = (params.get("orden") or "").strip()
    if orden in ORDENES:
        queryset = queryset.order_by(*ORDENES[orden])

    return queryset