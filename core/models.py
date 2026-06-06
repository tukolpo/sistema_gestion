# usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class Rol(models.Model):
    """
    Modelo para gestionar los roles y jerarquías del sistema de la DSI.
    """
    nombre = models.CharField(max_length=50, unique=True, help_text="Ej: Administrador, Supervisor, Oficial")
    # El nivel de jerarquía permite comparar permisos fácilmente (ej. >= 50)
    nivel_jerarquia = models.IntegerField(unique=True, help_text="Ej: 100 para Admin, 50 para Supervisor, 10 para Básico")
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['-nivel_jerarquia'] # Ordenar del rango más alto al más bajo

    def __str__(self):
        return f"{self.nombre} (Nivel {self.nivel_jerarquia})"

class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado extendiendo el de Django.
    Aquí asociamos la lógica de la Subtarea 3.2.
    """
    # Relación ForeignKey: Varios usuarios pueden tener un mismo rol.
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')
    cedula = models.CharField(max_length=15, unique=True, null=True, blank=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)

    def tiene_rango_minimo(self, nivel_requerido):
        """
        Método clave para validar si el usuario tiene permiso jerárquico.
        """
        # Los superusuarios de Django siempre tienen acceso
        if self.is_superuser:
            return True
        # Si tiene un rol asignado, evaluamos su jerarquía
        if self.rol:
            return self.rol.nivel_jerarquia >= nivel_requerido
        return False

    def __str__(self):
        return f"{self.username} - {self.rol.nombre if self.rol else 'Sin Rol'}"