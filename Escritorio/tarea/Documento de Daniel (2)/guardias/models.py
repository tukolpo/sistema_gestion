from django.db import models
from trabajadores.models import Trabajador

class Guardia(models.Model):
    nombre_turno = models.CharField(max_length=50)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        db_table = 'guardia'
        verbose_name = 'Guardia'
        verbose_name_plural = 'Guardias'

    def __str__(self):
        return f"{self.nombre_turno} ({self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')})"

class Cronograma(models.Model):
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    class Meta:
        db_table = 'cronograma'
        verbose_name = 'Cronograma'
        verbose_name_plural = 'Cronogramas'

    def __str__(self):
        return f"Cronograma: {self.fecha_inicio} a {self.fecha_fin}"

class AsignacionGuardia(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE)
    guardia = models.ForeignKey(Guardia, on_delete=models.CASCADE)
    cronograma = models.ForeignKey(Cronograma, on_delete=models.CASCADE)
    fecha = models.DateField()
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'asignacionguardia'
        verbose_name = 'Asignación de Guardia'
        verbose_name_plural = 'Asignaciones de Guardias'

    def __str__(self):
        return f"{self.trabajador} - {self.guardia} ({self.fecha})"

class AprobacionCronograma(models.Model):
    cronograma = models.OneToOneField(Cronograma, on_delete=models.CASCADE, related_name='aprobacion')
    aprobado = models.BooleanField(default=False)
    fecha_aprobacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Esto creará una tabla nueva en la BD real que se llama guardias_aprobacioncronograma
        verbose_name = 'Aprobación de Cronograma'
        verbose_name_plural = 'Aprobaciones de Cronogramas'

    def __str__(self):
        return f"Aprobación de {self.cronograma}"
