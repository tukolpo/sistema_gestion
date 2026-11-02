from dataclasses import dataclass
from datetime import date

import pandas as pd
from django.utils import timezone

from guardias.models import GuardiaTurno
from trabajadores.models import Trabajador
from vacaciones.models import SolicitudVacaciones

COLUMNAS_TRABAJADORES = [
    "id", "cedula", "nombre_completo", "cargo", "especialidad",
    "estado", "fecha_ingreso", "antiguedad_anios",
]

COLUMNAS_GUARDIAS = [
    "id", "trabajador_id", "cedula", "trabajador", "fecha", "turno", "aprobado",
]

COLUMNAS_VACACIONES = [
    "id", "trabajador_id", "cedula", "trabajador",
    "fecha_inicio", "fecha_fin", "dias", "estado",
]


class SinDatosError(Exception):
    """No hay datos para los filtros aplicados."""


@dataclass
class FiltrosReporte:
    cargo_id: int | None = None
    fecha_desde: date | None = None
    fecha_hasta: date | None = None

    @classmethod
    def desde_request(cls, request):
        def _fecha(valor):
            try:
                return date.fromisoformat(valor) if valor else None
            except ValueError:
                return None

        def _entero(valor):
            return int(valor) if valor and valor.isdigit() else None

        return cls(
            cargo_id=_entero(request.GET.get("cargo", "")),
            fecha_desde=_fecha(request.GET.get("fecha_desde", "")),
            fecha_hasta=_fecha(request.GET.get("fecha_hasta", "")),
        )


def exigir_datos(df, nombre="datos"):
    """Lanza SinDatosError si el DataFrame está vacío (caso sin resultados)."""
    if df.empty:
        raise SinDatosError(f"No se encontraron {nombre} con los filtros aplicados.")
    return df




def limpiar_trabajadores(df):
    """Limpia nulos, textos y fechas del DataFrame de trabajadores."""
    df = df.copy()
    df["nombre_completo"] = (
        df["nombre"].fillna("").str.strip() + " " + df["apellido"].fillna("").str.strip()
    ).str.strip().str.title()
    df = df.drop(columns=["nombre", "apellido"])

    for col in ["cedula", "cargo", "especialidad", "estado"]:
        df[col] = df[col].fillna("—").astype(str).str.strip()
        df.loc[df[col] == "", col] = "—"

    df["fecha_ingreso"] = pd.to_datetime(df["fecha_ingreso"], errors="coerce")
    hoy = pd.Timestamp(timezone.localdate())
    df["antiguedad_anios"] = (
        ((hoy - df["fecha_ingreso"]).dt.days / 365.25).round(1).fillna(0.0)
    )
    return df[COLUMNAS_TRABAJADORES]


def obtener_trabajadores_df(filtros=None):
    """DataFrame de trabajadores ya filtrado y limpio."""
    filtros = filtros or FiltrosReporte()
    qs = Trabajador.objects.all()
    if filtros.cargo_id:
        qs = qs.filter(cargo_id=filtros.cargo_id)
    if filtros.fecha_desde:
        qs = qs.filter(fecha_ingreso__gte=filtros.fecha_desde)
    if filtros.fecha_hasta:
        qs = qs.filter(fecha_ingreso__lte=filtros.fecha_hasta)

    filas = list(
        qs.values(
            "id", "cedula", "nombre", "apellido", "estado",
            "fecha_ingreso", "cargo__nombre", "especialidad__nombre",
        )
    )
    columnas_crudas = [
        "id", "cedula", "nombre", "apellido", "estado",
        "fecha_ingreso", "cargo", "especialidad",
    ]
    df = pd.DataFrame(filas)
    if df.empty:
        return pd.DataFrame(columns=COLUMNAS_TRABAJADORES)
    df = df.rename(columns={"cargo__nombre": "cargo", "especialidad__nombre": "especialidad"})
    return limpiar_trabajadores(df[columnas_crudas])




def _filtrar_por_trabajador(qs, filtros):
    """Aplica el filtro de cargo sobre el trabajador relacionado."""
    if filtros.cargo_id:
        qs = qs.filter(trabajador__cargo_id=filtros.cargo_id)
    return qs


def _limpiar_comunes(df):
    """Arma el nombre completo y rellena nulos de las columnas del trabajador."""
    df["trabajador"] = (
        df["nombre"].fillna("").str.strip() + " " + df["apellido"].fillna("").str.strip()
    ).str.strip().str.title()
    df = df.drop(columns=["nombre", "apellido"])
    df["cedula"] = df["cedula"].fillna("—").astype(str).str.strip()
    df.loc[df["cedula"] == "", "cedula"] = "—"
    return df


def obtener_guardias_df(filtros=None):
    """DataFrame de guardias/turnos ya filtrado y limpio."""
    filtros = filtros or FiltrosReporte()
    qs = _filtrar_por_trabajador(GuardiaTurno.objects.all(), filtros)
    if filtros.fecha_desde:
        qs = qs.filter(fecha__gte=filtros.fecha_desde)
    if filtros.fecha_hasta:
        qs = qs.filter(fecha__lte=filtros.fecha_hasta)

    filas = list(
        qs.order_by("fecha", "turno").values(
            "id", "trabajador_id", "trabajador__cedula", "trabajador__nombre",
            "trabajador__apellido", "fecha", "turno", "aprobado",
        )
    )
    if not filas:
        return pd.DataFrame(columns=COLUMNAS_GUARDIAS)

    df = pd.DataFrame(filas).rename(columns={
        "trabajador__cedula": "cedula",
        "trabajador__nombre": "nombre",
        "trabajador__apellido": "apellido",
    })
    df = _limpiar_comunes(df)
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    etiquetas_turno = dict(GuardiaTurno.TurnoOpcion.choices)
    df["turno"] = df["turno"].map(etiquetas_turno).fillna("—")
    df["aprobado"] = df["aprobado"].map({True: "Sí", False: "No"}).fillna("—")
    return df[COLUMNAS_GUARDIAS]


def obtener_vacaciones_df(filtros=None):
    """DataFrame de solicitudes de vacaciones ya filtrado y limpio."""
    filtros = filtros or FiltrosReporte()
    qs = _filtrar_por_trabajador(SolicitudVacaciones.objects.all(), filtros)
    # Una solicitud entra si su rango se cruza con el rango del filtro
    if filtros.fecha_desde:
        qs = qs.filter(fecha_fin__gte=filtros.fecha_desde)
    if filtros.fecha_hasta:
        qs = qs.filter(fecha_inicio__lte=filtros.fecha_hasta)

    filas = list(
        qs.order_by("-fecha_inicio").values(
            "id", "trabajador_id", "trabajador__cedula", "trabajador__nombre",
            "trabajador__apellido", "fecha_inicio", "fecha_fin",
            "dias_calculados", "estado",
        )
    )
    if not filas:
        return pd.DataFrame(columns=COLUMNAS_VACACIONES)

    df = pd.DataFrame(filas).rename(columns={
        "trabajador__cedula": "cedula",
        "trabajador__nombre": "nombre",
        "trabajador__apellido": "apellido",
        "dias_calculados": "dias",
    })
    df = _limpiar_comunes(df)
    df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], errors="coerce")
    df["fecha_fin"] = pd.to_datetime(df["fecha_fin"], errors="coerce")
    df["dias"] = df["dias"].fillna(0).astype(int)
    etiquetas_estado = dict(SolicitudVacaciones.Estado.choices)
    df["estado"] = df["estado"].map(etiquetas_estado).fillna("—")
    return df[COLUMNAS_VACACIONES]