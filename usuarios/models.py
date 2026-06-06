# usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    nivel_jerarquia = models.IntegerField(unique=True)
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

    def tiene_rango_minimo(self, nivel_requerido):
        if self.is_superuser:
            return True
        if self.rol:
            return self.rol.nivel_jerarquia >= nivel_requerido
        return False

    def __str__(self):
        return f"{self.username} - {self.rol.nombre if self.rol else 'Sin Rol'}"
