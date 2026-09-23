from django.db import models


class ConfiguracionGlobal(models.Model):
    nombre_sistema = models.CharField(max_length=100, default="Sistema de Gestión DSI")
    tiempo_sesion_minutos = models.PositiveIntegerField(default=30)
    dias_vacaciones_por_anio = models.PositiveIntegerField(default=15)
    max_intentos_login = models.PositiveIntegerField(default=5)
    minutos_bloqueo_login = models.PositiveIntegerField(default=5)
    modo_mantenimiento = models.BooleanField(default=False)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración Global"
        verbose_name_plural = "Configuración Global"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def obtener(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.nombre_sistema