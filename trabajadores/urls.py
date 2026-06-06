from django.urls import path
from . import views

app_name = "trabajadores"

urlpatterns = [
    path("", views.lista_trabajadores, name="lista"),
    path("nuevo/", views.crear_trabajador, name="crear"),
    path("<int:trabajador_id>/", views.detalle_trabajador, name="detalle"),
    path("<int:trabajador_id>/editar/", views.editar_trabajador, name="editar"),
    path("<int:trabajador_id>/estado/", views.cambiar_estado, name="estado"),
    path("<int:trabajador_id>/foto/", views.servir_foto, name="foto"),
    path(
        "documentos/<int:documento_id>/ver/",
        views.ver_documento,
        name="ver_documento",
    ),
    path(
        "documentos/<int:documento_id>/descargar/",
        views.descargar_documento,
        name="descargar_documento",
    ),
    path("perfil-publico/<uuid:trabajador_uuid>/", views.perfil_publico_trabajador, name="perfil_publico"),
]