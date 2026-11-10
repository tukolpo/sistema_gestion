from django.core.management.base import BaseCommand

from trabajadores.models import Especialidad


class Command(BaseCommand):
    help = "Crea especialidades por defecto si no existen."

    def handle(self, *args, **options):
        especialidades = ("Ninguna", "Seguridad", "Recursos Humanos", "Logística")

        for nombre in especialidades:
            Especialidad.objects.get_or_create(nombre=nombre)

        self.stdout.write(self.style.SUCCESS("Catálogo de especialidades listo."))