from datetime import date

import pandas as pd
from django.test import SimpleTestCase

from reportes.indicadores import (
    COLUMNAS_RESUMEN,
    HORAS_POR_TURNO,
    calcular_antiguedad_y_estado,
    calcular_horas_guardia_por_trabajador,
    calcular_vacaciones_por_departamento,
    construir_tabla_resumen,
)


def _trabajadores():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "cedula": ["001", "002", "003"],
        "nombre_completo": ["Ana Perez", "Luis Mora", "Eva Diaz"],
        "cargo": ["Analista", "Analista", "Tecnico"],
        "especialidad": ["Redes", "Redes", "Soporte"],
        "departamento": ["TI", "TI", "RRHH"],
        "estado": ["ACTIVO", "INACTIVO", "ACTIVO"],
        "fecha_ingreso": [date(2020, 1, 1), date(2022, 1, 1), date(2018, 1, 1)],
        "antiguedad_anios": [6.0, 4.0, 8.0],
    })


def _guardias():
    return pd.DataFrame({
        "id": [10, 11, 12, 13],
        "trabajador_id": [1, 1, 2, 3],
        "cedula": ["001", "001", "002", "003"],
        "trabajador": ["Ana Perez", "Ana Perez", "Luis Mora", "Eva Diaz"],
        "fecha": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-01", "2026-01-01"]),
        "turno": ["Mañana", "Noche", "Tarde", "Mañana"],
        "aprobado": ["Sí", "No", "Sí", "Sí"],
    })


def _vacaciones():
    return pd.DataFrame({
        "id": [20, 21, 22],
        "trabajador_id": [1, 1, 3],
        "cedula": ["001", "001", "003"],
        "trabajador": ["Ana Perez", "Ana Perez", "Eva Diaz"],
        "fecha_inicio": pd.to_datetime(["2026-02-01", "2026-07-01", "2026-03-01"]),
        "fecha_fin": pd.to_datetime(["2026-02-05", "2026-07-10", "2026-03-10"]),
        "dias": [5, 10, 10],
        "estado": ["Aprobada", "Pendiente", "Aprobada"],
    })


class IndicadoresPandasTests(SimpleTestCase):
    def test_horas_guardia_solo_cuentan_turnos_aprobados(self):
        resultado = calcular_horas_guardia_por_trabajador(_guardias())
        ana = resultado.loc[resultado["trabajador_id"] == 1].iloc[0]
        luis = resultado.loc[resultado["trabajador_id"] == 2].iloc[0]
        self.assertEqual(int(ana["turnos_cumplidos"]), 1)
        self.assertEqual(int(ana["horas_guardia_cumplidas"]), HORAS_POR_TURNO)
        self.assertEqual(int(luis["horas_guardia_cumplidas"]), HORAS_POR_TURNO)

    def test_vacaciones_usadas_y_disponibles_por_departamento(self):
        resultado = calcular_vacaciones_por_departamento(_trabajadores(), _vacaciones())
        ti = resultado.loc[resultado["departamento"] == "TI"].iloc[0]
        rrhh = resultado.loc[resultado["departamento"] == "RRHH"].iloc[0]
        # Ana: 6*15 - 5 = 85; Luis: 4*15 - 0 = 60; TI usados = 5, disponibles = 145
        self.assertEqual(int(ti["vacaciones_usadas"]), 5)
        self.assertEqual(int(ti["vacaciones_disponibles"]), 145)
        # Eva: 8*15 - 10 = 110
        self.assertEqual(int(rrhh["vacaciones_usadas"]), 10)
        self.assertEqual(int(rrhh["vacaciones_disponibles"]), 110)

    def test_antiguedad_promedio_y_conteos_de_estado(self):
        resultado = calcular_antiguedad_y_estado(_trabajadores()).iloc[0]
        self.assertEqual(resultado["trabajadores_activos"], 2)
        self.assertEqual(resultado["trabajadores_inactivos"], 1)
        self.assertEqual(resultado["total_trabajadores"], 3)
        self.assertEqual(resultado["antiguedad_promedio"], 6.0)

    def test_tabla_resumen_por_departamento(self):
        resumen = construir_tabla_resumen(_trabajadores(), _guardias(), _vacaciones())
        self.assertListEqual(list(resumen.columns), COLUMNAS_RESUMEN)
        ti = resumen.loc[resumen["departamento"] == "TI"].iloc[0]
        self.assertEqual(int(ti["trabajadores_activos"]), 1)
        self.assertEqual(int(ti["trabajadores_inactivos"]), 1)
        self.assertEqual(int(ti["horas_guardia_cumplidas"]), HORAS_POR_TURNO * 2)
        self.assertEqual(int(ti["vacaciones_usadas"]), 5)

    def test_dataframes_vacios_no_rompen_el_calculo(self):
        vacio = pd.DataFrame()
        horas = calcular_horas_guardia_por_trabajador(vacio)
        self.assertTrue(horas.empty)
        resumen = construir_tabla_resumen(vacio, vacio, vacio)
        self.assertTrue(resumen.empty)
        self.assertListEqual(list(resumen.columns), COLUMNAS_RESUMEN)
