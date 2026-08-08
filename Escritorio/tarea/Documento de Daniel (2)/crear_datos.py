import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from trabajadores.models import Trabajador
from guardias.models import Guardia
from usuarios.models import Usuario, Rol
from django.contrib.auth.hashers import make_password
import datetime

# Crear Rol
rol, _ = Rol.objects.get_or_create(nombre='Gerente de guardias', defaults={'nivel_jerarquia': 1})

# Crear Usuario
if not Usuario.objects.filter(username='admin').exists():
    Usuario.objects.create(
        username='admin',
        password=make_password('1234'),
        rol=rol,
        is_superuser=True,
        is_staff=True
    )

# Crear Guardias
if not Guardia.objects.exists():
    Guardia.objects.create(nombre_turno='Mañana', hora_inicio=datetime.time(6, 0), hora_fin=datetime.time(14, 0))
    Guardia.objects.create(nombre_turno='Tarde', hora_inicio=datetime.time(14, 0), hora_fin=datetime.time(22, 0))
    Guardia.objects.create(nombre_turno='Noche', hora_inicio=datetime.time(22, 0), hora_fin=datetime.time(6, 0))

from trabajadores.models import Trabajador, Cargo

# Crear Cargo
cargo, _ = Cargo.objects.get_or_create(nombre='Enfermero')

# Crear Trabajador
if not Trabajador.objects.exists():
    Trabajador.objects.create(
        nombre='Juan',
        apellido='Pérez',
        cedula='12345678',
        departamento='Urgencias',
        cargo=cargo,
        estado='ACTIVO'
    )
    Trabajador.objects.create(
        nombre='María',
        apellido='Gómez',
        cedula='87654321',
        departamento='Urgencias',
        cargo=cargo,
        estado='ACTIVO'
    )

print("Datos de prueba creados exitosamente.")
