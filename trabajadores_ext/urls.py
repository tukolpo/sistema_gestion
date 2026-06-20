from django.urls import path

from trabajadores_ext import views

app_name = "trabajadores_ext"

urlpatterns = [
    path("auditoria/", views.vista_auditoria, name="auditoria"),
    path("publico/<uuid:token>/", views.vista_perfil_publico, name="perfil_publico"),
    path("<int:trabajador_id>/qr/", views.vista_credencial_qr, name="credencial_qr"),
    path(
        "<int:trabajador_id>/qr/imagen/",
        views.vista_qr_imagen,
        name="qr_imagen",
    ),
]
