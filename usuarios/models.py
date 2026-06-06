# usuarios/models.py
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    nivel_jerarquia = models.IntegerField(
        help_text="100=Admin, 50=Gerente, 40=Supervisor, 20=Trabajador, 10=Funcionario",
    )
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ["-nivel_jerarquia"]

    def __str__(self):
        return f"{self.nombre} (Nivel {self.nivel_jerarquia})"


class Usuario(AbstractUser):
    rol = models.ForeignKey(
        Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name="usuarios"
    )
    cedula = models.CharField(max_length=15, unique=True, null=True, blank=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    intentos_fallidos_login = models.PositiveSmallIntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True, db_index=True)

    def esta_bloqueado(self):
        if self.bloqueado_hasta is None:
            return False
        if self.bloqueado_hasta <= timezone.now():
            return False
        return True

    def tiene_rango_minimo(self, nivel_requerido):
        if self.is_superuser:
            return True
        if self.rol:
            return self.rol.nivel_jerarquia >= nivel_requerido
        return False

    def __str__(self):
        return f"{self.username} - {self.rol.nombre if self.rol else 'Sin Rol'}"


class SecurityLog(models.Model):
    class Accion(models.TextChoices):
        LOGIN_SUCCESS = "login_success", "Login exitoso"
        LOGIN_FAILED = "login_failed", "Login fallido"
        ACCESS_DENIED = "access_denied", "Acceso denegado"

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="security_logs",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    action = models.CharField(max_length=20, choices=Accion.choices, db_index=True)
    user_agent = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Registro de seguridad"
        verbose_name_plural = "Registros de seguridad"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["-timestamp", "action"]),
        ]

    def __str__(self):
        usuario = self.user.username if self.user else "—"
        return f"{self.get_action_display()} · {usuario} · {self.timestamp:%Y-%m-%d %H:%M}"


class LogAuditoria(models.Model):
    class Accion(models.TextChoices):
        CREAR = "CREAR", "Creación"
        EDITAR = "EDITAR", "Edición"
        ELIMINAR = "ELIMINAR", "Eliminación"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs_auditoria",
    )
    accion = models.CharField(max_length=10, choices=Accion.choices, db_index=True)
    modelo_afectado = models.CharField(max_length=100)
    registro_id = models.CharField(max_length=255)
    valores_anteriores = models.JSONField(null=True, blank=True)
    valores_nuevos = models.JSONField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "Log de Auditoría"
        verbose_name_plural = "Logs de Auditoría"
        ordering = ["-fecha"]
        indexes = [
            models.Index(fields=["-fecha", "modelo_afectado"]),
        ]

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Sistema"
        return f"[{self.fecha:%Y-%m-%d %H:%M}] {usuario_str} -> {self.get_accion_display()} {self.modelo_afectado} (ID: {self.registro_id})"
