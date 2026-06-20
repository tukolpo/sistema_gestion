# trabajadores/filters.py
# Motor de filtrado inteligente — Módulo 3, Tarea 1

from datetime import date

from django.db.models import Q
from django.utils import timezone

from trabajadores.models import Trabajador


def _fecha_limite_antiguedad(anios: int) -> date:
    hoy = timezone.now().date()
    try:
        return hoy.replace(year=hoy.year - anios)
    except ValueError:
        return hoy.replace(year=hoy.year - anios, day=28)


def aplicar_filtros_trabajadores(queryset, params):
    """
    Aplica filtros opcionales y combinables sobre un queryset de Trabajador.
    Parámetros soportados: cargo, departamento, estatus (o estado), antiguedad.
    """
    filtros = Q()

    cargo = (params.get("cargo") or "").strip()
    if cargo:
        if cargo.isdigit():
            filtros &= Q(cargo_id=int(cargo))
        else:
            filtros &= Q(cargo__nombre__icontains=cargo)

    departamento = (params.get("departamento") or "").strip()
    if departamento:
        filtros &= Q(departamento__icontains=departamento)

    estatus = (params.get("estatus") or params.get("estado") or "").strip()
    if estatus in Trabajador.Estado.values:
        filtros &= Q(estado=estatus)

    antiguedad = (params.get("antiguedad") or "").strip()
    if antiguedad.isdigit():
        anios = int(antiguedad)
        if anios >= 0:
            fecha_limite = _fecha_limite_antiguedad(anios)
            filtros &= Q(
                fecha_ingreso__isnull=False,
                fecha_ingreso__lte=fecha_limite,
            )

    if filtros:
        queryset = queryset.filter(filtros)

    return queryset
