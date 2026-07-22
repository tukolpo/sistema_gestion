from django.db import models


class VacacionSolicitud(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        APROBADA = "APROBADA", "Aprobada"
        RECHAZADA = "RECHAZADA", "Rechazada"

    trabajador = models.ForeignKey(
        "trabajadores.Trabajador",
        on_delete=models.CASCADE,
        related_name="vacaciones",
    )
    fecha_solicitud = models.DateField(auto_now_add=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_solicitados = models.PositiveSmallIntegerField(null=True, blank=True)
    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        db_index=True,
    )

    class Meta:
        verbose_name = "Solicitud de vacaciones"
        verbose_name_plural = "Solicitudes de vacaciones"
        ordering = ["-fecha_inicio"]

    def __str__(self):
        return f"Vacaciones {self.trabajador} ({self.fecha_inicio} – {self.fecha_fin})"


class PermisoLaboral(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        APROBADO = "APROBADO", "Aprobado"
        RECHAZADO = "RECHAZADO", "Rechazado"

    trabajador = models.ForeignKey(
        "trabajadores.Trabajador",
        on_delete=models.CASCADE,
        related_name="permisos_laborales",
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.CharField(max_length=200, blank=True)
    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        db_index=True,
    )

    class Meta:
        verbose_name = "Permiso laboral"
        verbose_name_plural = "Permisos laborales"
        ordering = ["-fecha_inicio"]

    def __str__(self):
        return f"Permiso {self.trabajador} ({self.fecha_inicio} – {self.fecha_fin})"
