# trabajadores/api_urls.py
# Rutas API del módulo trabajadores

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from trabajadores.api_views import (
    CargoViewSet,
    DocumentoTrabajadorViewSet,
    EspecialidadViewSet,
    TrabajadorViewSet,
)

router = DefaultRouter()
router.register("cargos", CargoViewSet, basename="cargo")
router.register("especialidades", EspecialidadViewSet, basename="especialidad")
router.register("documentos", DocumentoTrabajadorViewSet, basename="documento")
router.register("", TrabajadorViewSet, basename="trabajador")

urlpatterns = [
    path("", include(router.urls)),
]
