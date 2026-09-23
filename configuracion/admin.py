from django.contrib import admin
from .models import ConfiguracionGlobal


@admin.register(ConfiguracionGlobal)
class ConfiguracionGlobalAdmin(admin.ModelAdmin):
    list_display = ("nombre_sistema", "tiempo_sesion_minutos", "modo_mantenimiento")