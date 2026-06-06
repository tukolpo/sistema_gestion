from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Rol, SecurityLog, Usuario


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nivel_jerarquia", "fecha_creacion")
    search_fields = ("nombre",)
    ordering = ("-nivel_jerarquia",)


@admin.register(Usuario)
class UsuarioPersonalizadoAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Información DSI y RBAC", {"fields": ("rol", "cedula", "departamento")}),
        (
            "Seguridad de acceso",
            {"fields": ("intentos_fallidos_login", "bloqueado_hasta")},
        ),
    )
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "rol",
        "is_staff",
        "intentos_fallidos_login",
        "bloqueado_hasta",
    )
    list_filter = ("rol", "is_staff", "is_superuser")


@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "action", "user", "ip_address", "user_agent_corto")
    list_filter = ("action", "timestamp")
    search_fields = ("user__username", "user__email", "ip_address")
    readonly_fields = (
        "timestamp",
        "user",
        "ip_address",
        "action",
        "user_agent",
    )
    date_hierarchy = "timestamp"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    @admin.display(description="User-Agent")
    def user_agent_corto(self, obj):
        if len(obj.user_agent) > 60:
            return f"{obj.user_agent[:60]}…"
        return obj.user_agent
