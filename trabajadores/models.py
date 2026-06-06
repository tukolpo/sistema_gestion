import uuid

from django.conf import settings
from django.db import models

from trabajadores.storage import private_storage


def _ruta_foto(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    carpeta = instance.pk or uuid.uuid4().hex[:12]
    return f"trabajadores/{carpeta}/fotos/perfil.{ext}"


def _ruta_documento(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    return (
        f"trabajadores/{instance.trabajador_id}/documentos/"
        f"{uuid.uuid4().hex}_{instance.tipo}.{ext}"
    )


class Cargo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Especialidad"
        verbose_name_plural = "Especialidades"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Trabajador(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        INACTIVO = "INACTIVO", "Inactivo"

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=15, unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    departamento = models.CharField(max_length=100)
    cargo = models.ForeignKey(
        Cargo, on_delete=models.PROTECT, related_name="trabajadores"
    )
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trabajadores",
    )
    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.ACTIVO,
        db_index=True,
    )
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    notas_perfil = models.TextField(blank=True, verbose_name="Notas del perfil")
    foto = models.ImageField(
        upload_to=_ruta_foto,
        storage=private_storage,
        null=True,
        blank=True,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Trabajador"
        verbose_name_plural = "Trabajadores"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def esta_activo(self):
        return self.estado == self.Estado.ACTIVO

    def activar(self):
        self.estado = self.Estado.ACTIVO
        self.save(update_fields=["estado", "fecha_actualizacion"])

    def desactivar(self):
        self.estado = self.Estado.INACTIVO
        self.save(update_fields=["estado", "fecha_actualizacion"])

    def alternar_estado(self):
        if self.esta_activo:
            self.desactivar()
        else:
            self.activar()


class DocumentoTrabajador(models.Model):
    class Tipo(models.TextChoices):
        CEDULA = "CEDULA", "Cédula"
        CONTRATO = "CONTRATO", "Contrato"
        CERTIFICADO = "CERTIFICADO", "Certificado"
        OTRO = "OTRO", "Otro"

    trabajador = models.ForeignKey(
        Trabajador, on_delete=models.CASCADE, related_name="documentos"
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.OTRO)
    titulo = models.CharField(max_length=150)
    archivo = models.FileField(
        upload_to=_ruta_documento,
        storage=private_storage,
    )
    subido_en = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documentos_trabajador_subidos",
    )

    class Meta:
        verbose_name = "Documento de trabajador"
        verbose_name_plural = "Documentos de trabajadores"
        ordering = ["-subido_en"]

    def __str__(self):
        return f"{self.titulo} ({self.trabajador})"

    @property
    def extension(self):
        return self.archivo.name.rsplit(".", 1)[-1].lower()
