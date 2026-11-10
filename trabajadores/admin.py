from django.contrib import admin

from .models import DocumentoTrabajador, Especialidad, Trabajador


@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    search_fields = ("nombre",)


class DocumentoInline(admin.TabularInline):
    model = DocumentoTrabajador
    extra = 0
    readonly_fields = ("subido_en", "subido_por")


@admin.register(Trabajador)
class TrabajadorAdmin(admin.ModelAdmin):
    list_display = (
        "apellido",
        "nombre",
        "cedula",
        "especialidad",
        "departamento",
        "estado",
        "fecha_ingreso",
    )
    list_filter = ("estado", "departamento", "especialidad")
    search_fields = ("nombre", "apellido", "cedula", "email")
    ordering = ("apellido", "nombre")
    inlines = [DocumentoInline]


@admin.register(DocumentoTrabajador)
class DocumentoTrabajadorAdmin(admin.ModelAdmin):
    list_display = ("titulo", "trabajador", "tipo", "subido_en", "subido_por")
    list_filter = ("tipo",)