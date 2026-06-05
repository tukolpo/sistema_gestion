from django.core.management.base import BaseCommand

from trabajadores.models import Cargo, Especialidad


class Command(BaseCommand):
    help = "Crea cargos y especialidades por defecto si no existen."

    def handle(self, *args, **options):
        cargos = ("General", "Administrativo", "Operativo", "Supervisor")
        especialidades = ("Ninguna", "Seguridad", "Recursos Humanos", "Logística")

        for nombre in cargos:
            Cargo.objects.get_or_create(nombre=nombre)
        for nombre in especialidades:
            Especialidad.objects.get_or_create(nombre=nombre)

        self.stdout.write(self.style.SUCCESS("Catálogos de cargo y especialidad listos."))
