from django.db import models
from trabajadores.models import Trabajador

class SolicitudVacaciones(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        APROBADA = "APROBADA", "Aprobada"
        RECHAZADA = "RECHAZADA", "Rechazada"

    trabajador = models.ForeignKey(
        Trabajador, 
        on_delete=models.CASCADE, 
        related_name="solicitudes_vacaciones",
        verbose_name="Trabajador"
    )
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Fin")
    dias_calculados = models.PositiveIntegerField(verbose_name="Días Calculados", editable=False)
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        db_index=True,
        verbose_name="Estado"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Solicitud de Vacaciones"
        verbose_name_plural = "Solicitudes de Vacaciones"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"Vacaciones de {self.trabajador} ({self.fecha_inicio} al {self.fecha_fin})"

    def save(self, *args, **kwargs):
       
        if self.fecha_inicio and self.fecha_fin:
            delta = self.fecha_fin - self.fecha_inicio
            self.dias_calculados = max(delta.days + 1, 1)
        super().save(*args, **kwargs)