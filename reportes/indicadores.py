"""Indicadores de reportes (Módulo 7, Tarea 2) a partir de los DataFrames base."""

from __future__ import annotations

import numpy as np
import pandas as pd

from vacaciones.services import DIAS_POR_ANIO

from reportes.datos import (
    obtener_guardias_df,
    obtener_trabajadores_df,
    obtener_vacaciones_df,
)

HORAS_POR_TURNO = 8
ESTADO_ACTIVO = "ACTIVO"
ESTADO_INACTIVO = "INACTIVO"
VACACIONES_APROBADAS = "Aprobada"
GUARDIA_APROBADA = "Sí"

COLUMNAS_HORAS = [
    "trabajador_id", "cedula", "trabajador",
    "turnos_cumplidos", "horas_guardia_cumplidas",
]
COLUMNAS_VACACIONES_DEPTO = [
    "departamento", "vacaciones_usadas", "vacaciones_disponibles",
]
COLUMNAS_ANTIGUEDAD_ESTADO = [
    "antiguedad_promedio", "trabajadores_activos", "trabajadores_inactivos", "total_trabajadores",
]
COLUMNAS_RESUMEN = [
    "departamento",
    "trabajadores_activos",
    "trabajadores_inactivos",
    "total_trabajadores",
    "antiguedad_promedio",
    "horas_guardia_cumplidas",
    "vacaciones_usadas",
    "vacaciones_disponibles",
]


def _vacio(columnas):
    return pd.DataFrame(columns=columnas)


def calcular_horas_guardia_por_trabajador(df_guardias):
    """Horas de guardia cumplidas (turnos aprobados) agrupadas por trabajador."""
    if df_guardias is None or df_guardias.empty:
        return _vacio(COLUMNAS_HORAS)

    df = df_guardias.copy()
    df["horas"] = np.where(df["aprobado"] == GUARDIA_APROBADA, HORAS_POR_TURNO, 0)
    df["turno_cumplido"] = (df["aprobado"] == GUARDIA_APROBADA).astype(int)

    resumen = (
        df.groupby(["trabajador_id", "cedula", "trabajador"], as_index=False)
        .agg(
            turnos_cumplidos=("turno_cumplido", "sum"),
            horas_guardia_cumplidas=("horas", "sum"),
        )
        .sort_values(["trabajador", "cedula"], ignore_index=True)
    )
    return resumen[COLUMNAS_HORAS]


def _vacaciones_por_trabajador(df_trabajadores, df_vacaciones):
    """Días usados (aprobados) y disponibles por trabajador."""
    base = df_trabajadores[["id", "departamento", "antiguedad_anios"]].copy()
    base = base.rename(columns={"id": "trabajador_id"})
    base["departamento"] = base["departamento"].fillna("—").replace("", "—")
    base["anios_completos"] = np.floor(base["antiguedad_anios"].fillna(0)).astype(int).clip(lower=0)
    base["dias_totales"] = base["anios_completos"] * DIAS_POR_ANIO

    if df_vacaciones is None or df_vacaciones.empty:
        usados = pd.DataFrame(columns=["trabajador_id", "vacaciones_usadas"])
    else:
        aprobadas = df_vacaciones[df_vacaciones["estado"] == VACACIONES_APROBADAS]
        usados = (
            aprobadas.groupby("trabajador_id", as_index=False)["dias"]
            .sum()
            .rename(columns={"dias": "vacaciones_usadas"})
        )

    df = base.merge(usados, on="trabajador_id", how="left")
    df["vacaciones_usadas"] = df["vacaciones_usadas"].fillna(0).astype(int)
    df["vacaciones_disponibles"] = (df["dias_totales"] - df["vacaciones_usadas"]).clip(lower=0)
    return df


def calcular_vacaciones_por_departamento(df_trabajadores, df_vacaciones):
    """Vacaciones usadas y disponibles agrupadas por departamento."""
    if df_trabajadores is None or df_trabajadores.empty:
        return _vacio(COLUMNAS_VACACIONES_DEPTO)

    por_trabajador = _vacaciones_por_trabajador(df_trabajadores, df_vacaciones)
    resumen = (
        por_trabajador.groupby("departamento", as_index=False)
        .agg(
            vacaciones_usadas=("vacaciones_usadas", "sum"),
            vacaciones_disponibles=("vacaciones_disponibles", "sum"),
        )
        .sort_values("departamento", ignore_index=True)
    )
    resumen["vacaciones_usadas"] = resumen["vacaciones_usadas"].astype(int)
    resumen["vacaciones_disponibles"] = resumen["vacaciones_disponibles"].astype(int)
    return resumen[COLUMNAS_VACACIONES_DEPTO]


def calcular_antiguedad_y_estado(df_trabajadores):
    """Antigüedad promedio y totales de activos/inactivos (indicadores globales)."""
    if df_trabajadores is None or df_trabajadores.empty:
        return pd.DataFrame([{
            "antiguedad_promedio": 0.0,
            "trabajadores_activos": 0,
            "trabajadores_inactivos": 0,
            "total_trabajadores": 0,
        }])

    activos = (df_trabajadores["estado"] == ESTADO_ACTIVO).sum()
    inactivos = (df_trabajadores["estado"] == ESTADO_INACTIVO).sum()
    return pd.DataFrame([{
        "antiguedad_promedio": round(float(df_trabajadores["antiguedad_anios"].fillna(0).mean()), 2),
        "trabajadores_activos": int(activos),
        "trabajadores_inactivos": int(inactivos),
        "total_trabajadores": int(len(df_trabajadores)),
    }])[COLUMNAS_ANTIGUEDAD_ESTADO]


def construir_tabla_resumen(df_trabajadores, df_guardias, df_vacaciones):
    """Tabla resumen por departamento, lista para el sistema de reportes."""
    if df_trabajadores is None or df_trabajadores.empty:
        return _vacio(COLUMNAS_RESUMEN)

    base = df_trabajadores.copy()
    base["departamento"] = base["departamento"].fillna("—").replace("", "—")

    plantilla = (
        base.groupby("departamento", as_index=False)
        .agg(
            trabajadores_activos=("estado", lambda s: int((s == ESTADO_ACTIVO).sum())),
            trabajadores_inactivos=("estado", lambda s: int((s == ESTADO_INACTIVO).sum())),
            total_trabajadores=("id", "count"),
            antiguedad_promedio=("antiguedad_anios", "mean"),
        )
    )
    plantilla["antiguedad_promedio"] = plantilla["antiguedad_promedio"].fillna(0).round(2)

    horas = calcular_horas_guardia_por_trabajador(df_guardias)
    if horas.empty:
        horas_depto = pd.DataFrame(columns=["departamento", "horas_guardia_cumplidas"])
    else:
        horas_depto = (
            base[["id", "departamento"]]
            .rename(columns={"id": "trabajador_id"})
            .merge(horas[["trabajador_id", "horas_guardia_cumplidas"]], on="trabajador_id", how="left")
        )
        horas_depto["horas_guardia_cumplidas"] = horas_depto["horas_guardia_cumplidas"].fillna(0)
        horas_depto = (
            horas_depto.groupby("departamento", as_index=False)["horas_guardia_cumplidas"]
            .sum()
        )

    vacaciones = calcular_vacaciones_por_departamento(base, df_vacaciones)

    resumen = (
        plantilla
        .merge(horas_depto, on="departamento", how="left")
        .merge(vacaciones, on="departamento", how="left")
        .sort_values("departamento", ignore_index=True)
    )
    for col in ["horas_guardia_cumplidas", "vacaciones_usadas", "vacaciones_disponibles"]:
        resumen[col] = resumen[col].fillna(0).astype(int)
    return resumen[COLUMNAS_RESUMEN]


def calcular_indicadores(filtros=None):
    """Carga los DataFrames base y calcula todos los indicadores del reporte."""
    df_trabajadores = obtener_trabajadores_df(filtros)
    df_guardias = obtener_guardias_df(filtros)
    df_vacaciones = obtener_vacaciones_df(filtros)

    horas = calcular_horas_guardia_por_trabajador(df_guardias)
    vacaciones = calcular_vacaciones_por_departamento(df_trabajadores, df_vacaciones)
    antiguedad = calcular_antiguedad_y_estado(df_trabajadores)
    resumen = construir_tabla_resumen(df_trabajadores, df_guardias, df_vacaciones)

    return {
        "horas_por_trabajador": horas,
        "vacaciones_por_departamento": vacaciones,
        "antiguedad_y_estado": antiguedad,
        "resumen": resumen,
    }
