from django.core.management.base import BaseCommand

from trabajadores.models import Trabajador
from trabajadores_ext.models import TrabajadorTokenQR


class Command(BaseCommand):
    help = "Genera tokens QR para trabajadores que aún no tienen uno."

    def handle(self, *args, **options):
        creados = 0
        for trabajador in Trabajador.objects.all():
            _, created = TrabajadorTokenQR.objects.get_or_create(trabajador=trabajador)
            if created:
                creados += 1
        self.stdout.write(self.style.SUCCESS(f"Tokens listos. Nuevos: {creados}"))
