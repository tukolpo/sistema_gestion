from django.contrib import admin

from trabajadores_ext.models import AuditoriaTrabajador, EscaneoQR, TrabajadorTokenQR


@admin.register(TrabajadorTokenQR)
class TrabajadorTokenQRAdmin(admin.ModelAdmin):
    list_display = ("trabajador", "token", "activo", "generado_en")
    search_fields = ("trabajador__nombre", "trabajador__cedula", "token")
    list_filter = ("activo",)


@admin.register(EscaneoQR)
class EscaneoQRAdmin(admin.ModelAdmin):
    list_display = ("token_qr", "ip", "escaneado_en")
    list_filter = ("escaneado_en",)


@admin.register(AuditoriaTrabajador)
class AuditoriaTrabajadorAdmin(admin.ModelAdmin):
    list_display = ("accion", "trabajador", "usuario", "tabla", "creado_en")
    list_filter = ("accion", "tabla")
    search_fields = ("trabajador__cedula", "usuario__username", "valor_nuevo")
    readonly_fields = (
        "trabajador",
        "usuario",
        "accion",
        "tabla",
        "registro_id",
        "valor_anterior",
        "valor_nuevo",
        "ip",
        "user_agent",
        "ruta",
        "creado_en",
    )
