from django.db import models
from datetime import date
from dateutil.relativedelta import relativedelta

from .models import SolicitudVacaciones

DIAS_POR_ANIO = 15


def calcular_anios_trabajados(fecha_ingreso, fecha_referencia=None):
    fecha_referencia = fecha_referencia or date.today()
    delta = relativedelta(fecha_referencia, fecha_ingreso)
    return delta.years


def calcular_dias_disponibles(trabajador, fecha_referencia=None):
    fecha_referencia = fecha_referencia or date.today()

    if not trabajador.fecha_ingreso:
        return {
            "anios_trabajados": 0,
            "dias_totales": 0,
            "dias_usados": 0,
            "dias_disponibles": 0,
        }

    anios_trabajados = calcular_anios_trabajados(trabajador.fecha_ingreso, fecha_referencia)
    dias_totales = anios_trabajados * DIAS_POR_ANIO

    dias_usados = SolicitudVacaciones.objects.filter(
        trabajador=trabajador,
        estado=SolicitudVacaciones.Estado.APROBADA,
    ).aggregate(total=models.Sum("dias_calculados"))["total"] or 0

    dias_disponibles = max(dias_totales - dias_usados, 0)

    return {
        "anios_trabajados": anios_trabajados,
        "dias_totales": dias_totales,
        "dias_usados": dias_usados,
        "dias_disponibles": dias_disponibles,
    }