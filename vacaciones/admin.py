from django.contrib import admin
from .models import SolicitudVacaciones

@admin.register(SolicitudVacaciones)
class SolicitudVacacionesAdmin(admin.ModelAdmin):
    list_display = (
        "trabajador", 
        "fecha_inicio", 
        "fecha_fin", 
        "dias_calculados", 
        "estado", 
        "fecha_creacion"
    )
    list_filter = ("estado", "fecha_inicio")
    search_fields = (
        "trabajador__nombre", 
        "trabajador__apellido", 
        "trabajador__cedula"
    )
    ordering = ("-fecha_creacion",)