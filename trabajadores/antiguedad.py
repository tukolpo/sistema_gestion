"""Antigüedad exacta de un trabajador (años, meses y días por calendario)."""
import calendar
from datetime import date

from django.utils import timezone


def desglose_antiguedad(fecha_ingreso, hoy=None):
    """Devuelve (años, meses, días) transcurridos desde fecha_ingreso."""
    hoy = hoy or timezone.localdate()
    if not fecha_ingreso or fecha_ingreso > hoy:
        return 0, 0, 0
    años = hoy.year - fecha_ingreso.year
    meses = hoy.month - fecha_ingreso.month
    dias = hoy.day - fecha_ingreso.day
    if dias < 0:
        meses -= 1
        mes_prev = hoy.month - 1 or 12
        año_prev = hoy.year if hoy.month > 1 else hoy.year - 1
        dias += calendar.monthrange(año_prev, mes_prev)[1]
    if meses < 0:
        años -= 1
        meses += 12
    return años, meses, dias


def texto_antiguedad(fecha_ingreso, hoy=None):
    """Texto legible: '1 año, 2 meses y 5 días'. '—' si no hay fecha."""
    if not fecha_ingreso:
        return "—"
    años, meses, dias = desglose_antiguedad(fecha_ingreso, hoy)
    partes = []
    if años:
        partes.append(f"{años} año" + ("s" if años != 1 else ""))
    if meses:
        partes.append(f"{meses} mes" + ("es" if meses != 1 else ""))
    if dias:
        partes.append(f"{dias} día" + ("s" if dias != 1 else ""))
    if not partes:
        return "Ingresó hoy"
    if len(partes) == 1:
        return partes[0]
    return ", ".join(partes[:-1]) + " y " + partes[-1]


MAYORIA_DE_EDAD = 18


def fecha_limite_mayoria(hoy=None):
    """Fecha de nacimiento más reciente que aún es mayor de edad."""
    hoy = hoy or timezone.localdate()
    try:
        return hoy.replace(year=hoy.year - MAYORIA_DE_EDAD)
    except ValueError:  # 29 de febrero
        return hoy.replace(year=hoy.year - MAYORIA_DE_EDAD, day=28)


def es_mayor_de_edad(fecha_nacimiento, hoy=None):
    return fecha_nacimiento <= fecha_limite_mayoria(hoy)