from django.urls import path
from . import views

app_name = "vacaciones"

urlpatterns = [
    path("", views.gestion_vacaciones, name="gestion_vacaciones"),
    path("solicitar/", views.crear_solicitud, name="crear_solicitud"),
    path("solicitudes/", views.lista_solicitudes, name="lista_solicitudes"),
    path("solicitudes/<int:solicitud_id>/estado/", views.cambiar_estado_solicitud, name="cambiar_estado_solicitud"),
]