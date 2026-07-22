from django.contrib import admin

from guardias.models import PermisoLaboral, VacacionSolicitud


@admin.register(VacacionSolicitud)
class VacacionSolicitudAdmin(admin.ModelAdmin):
    list_display = ("trabajador", "fecha_inicio", "fecha_fin", "estado", "fecha_solicitud")
    list_filter = ("estado",)
    search_fields = ("trabajador__nombre", "trabajador__apellido", "trabajador__cedula")


@admin.register(PermisoLaboral)
class PermisoLaboralAdmin(admin.ModelAdmin):
    list_display = ("trabajador", "fecha_inicio", "fecha_fin", "estado", "motivo")
    list_filter = ("estado",)
    search_fields = ("trabajador__nombre", "trabajador__apellido", "trabajador__cedula")
