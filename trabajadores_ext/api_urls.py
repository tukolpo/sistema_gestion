from django.urls import include, path
from rest_framework.routers import DefaultRouter

from trabajadores_ext.api_views import AuditoriaTrabajadorViewSet, TrabajadorQRViewSet

router = DefaultRouter()
router.register("auditoria", AuditoriaTrabajadorViewSet, basename="auditoria")
router.register("qr", TrabajadorQRViewSet, basename="qr")

urlpatterns = [
    path("", include(router.urls)),
]
