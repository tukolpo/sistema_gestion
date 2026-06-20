import uuid

from django.conf import settings
from django.db import models


class TrabajadorTokenQR(models.Model):
    trabajador = models.OneToOneField(
        "trabajadores.Trabajador",
        on_delete=models.CASCADE,
        related_name="token_qr",
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    activo = models.BooleanField(default=True)
    generado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Token QR de trabajador"
        verbose_name_plural = "Tokens QR de trabajadores"

    def __str__(self):
        return str(self.token)


class EscaneoQR(models.Model):
    token_qr = models.ForeignKey(
        TrabajadorTokenQR,
        on_delete=models.CASCADE,
        related_name="escaneos",
    )
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")
    escaneado_en = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Escaneo QR"
        verbose_name_plural = "Escaneos QR"
        ordering = ["-escaneado_en"]


class AuditoriaTrabajador(models.Model):
    class Accion(models.TextChoices):
        CREAR = "CREAR", "Crear"
        ACTUALIZAR = "ACTUALIZAR", "Actualizar"
        ELIMINAR = "ELIMINAR", "Eliminar"
        ESTADO = "ESTADO", "Cambio de estado"
        DOCUMENTO = "DOCUMENTO", "Documento"
        QR_GENERADO = "QR_GENERADO", "QR generado"
        QR_ESCANEADO = "QR_ESCANEADO", "QR escaneado"
        ACCESO = "ACCESO", "Acceso"

    trabajador = models.ForeignKey(
        "trabajadores.Trabajador",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auditorias",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auditorias_trabajadores",
    )
    accion = models.CharField(max_length=20, choices=Accion.choices, db_index=True)
    tabla = models.CharField(max_length=80, blank=True, default="")
    registro_id = models.PositiveIntegerField(null=True, blank=True)
    valor_anterior = models.TextField(blank=True, default="")
    valor_nuevo = models.TextField(blank=True, default="")
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")
    ruta = models.CharField(max_length=255, blank=True, default="")
    creado_en = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Auditoría de trabajador"
        verbose_name_plural = "Auditorías de trabajadores"
        ordering = ["-creado_en"]
        indexes = [
            models.Index(fields=["-creado_en", "accion"]),
            models.Index(fields=["tabla", "registro_id"]),
        ]

    def __str__(self):
        return f"{self.accion} · {self.creado_en:%Y-%m-%d %H:%M}"
