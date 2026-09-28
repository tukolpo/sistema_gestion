from django.urls import path

from guardias.api_views import (
    DisponibilidadAPIView,
    AsignarTurnoAPIView,
    CronogramaSemanalAPIView,
    ExportarReporteGuardiasView,
    MisGuardiasAPIView,
)

urlpatterns = [
    path("disponibilidad/", DisponibilidadAPIView.as_view(), name="disponibilidad"),
    path("asignar/", AsignarTurnoAPIView.as_view(), name="asignar_turno"),
    path("cronograma/", CronogramaSemanalAPIView.as_view(), name="cronograma_semanal"),
    path("reporte/", ExportarReporteGuardiasView.as_view(), name="reporte_guardias"),
    path("mis-guardias/", MisGuardiasAPIView.as_view(), name="mis_guardias"),
]