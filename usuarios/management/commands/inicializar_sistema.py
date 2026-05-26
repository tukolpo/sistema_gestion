"""
Crea roles y usuario administrador en las tablas Django (usuarios_rol / usuarios_usuario).

Uso:
    python manage.py inicializar_sistema
    python manage.py inicializar_sistema --reset-admin-password
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection

from usuarios.constants import ROLES_INICIALES, NIVEL_ADMINISTRADOR
from usuarios.models import Rol

Usuario = get_user_model()

ADMIN_EMAIL = "admin@dsi.local"
ADMIN_PASSWORD = "Admin1234"


class Command(BaseCommand):
    help = "Inicializa roles RBAC y usuario administrador del Módulo 1 (Django)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-admin-password",
            action="store_true",
            help="Restablece la contraseña del administrador a la de desarrollo.",
        )

    def handle(self, *args, **options):
        self._crear_roles()
        admin = self._crear_admin(options["reset_admin_password"])
        self._resumen(admin)

    def _crear_roles(self):
        self._sincronizar_secuencia("usuarios_rol")
        for datos in ROLES_INICIALES:
            rol = Rol.objects.filter(nombre=datos["nombre"]).first()
            if rol:
                rol.nivel_jerarquia = datos["nivel_jerarquia"]
                rol.descripcion = datos["descripcion"]
                rol.save()
                accion = "Actualizado"
            else:
                rol = Rol.objects.create(
                    nombre=datos["nombre"],
                    nivel_jerarquia=datos["nivel_jerarquia"],
                    descripcion=datos["descripcion"],
                )
                accion = "Creado"
            self.stdout.write(
                f"  {accion}: {rol.nombre} (nivel {rol.nivel_jerarquia})"
            )
        self._sincronizar_secuencia("usuarios_rol")

    def _sincronizar_secuencia(self, tabla):
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT setval(
                    pg_get_serial_sequence('{tabla}', 'id'),
                    COALESCE((SELECT MAX(id) FROM {tabla}), 1)
                )
                """
            )

    def _crear_admin(self, reset_password):
        rol_admin = Rol.objects.get(
            nombre="Administrador", nivel_jerarquia=NIVEL_ADMINISTRADOR
        )

        usuario = Usuario.objects.filter(email=ADMIN_EMAIL).first()
        if usuario is None:
            usuario = Usuario.objects.filter(username=ADMIN_EMAIL).first()

        creado = usuario is None
        if creado:
            usuario = Usuario(
                email=ADMIN_EMAIL,
                username="admin",
                first_name="Administrador",
            )

        if creado or reset_password:
            usuario.set_password(ADMIN_PASSWORD)

        usuario.email = ADMIN_EMAIL
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.rol = rol_admin
        usuario.is_active = True
        usuario.save()

        if creado or reset_password:
            self.stdout.write(
                self.style.SUCCESS("  Administrador listo (contraseña configurada).")
            )
        else:
            self.stdout.write("  Administrador existente (contraseña sin cambios).")

        self._sincronizar_secuencia("usuarios_usuario")
        return usuario

    def _resumen(self, admin):
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Sistema listo (Módulo 1 — Django)"))
        self.stdout.write("")
        self.stdout.write("  Login web:  http://127.0.0.1:8000/")
        self.stdout.write(f"  Correo:     {ADMIN_EMAIL}")
        self.stdout.write(f"  Contraseña: {ADMIN_PASSWORD}")
        self.stdout.write("")
        self.stdout.write("  API JWT:    POST /api/auth/login/")
        self.stdout.write(
            f'  Body:       {{"username": "{ADMIN_EMAIL}", "password": "{ADMIN_PASSWORD}"}}'
        )
        self.stdout.write("")
        self.stdout.write(
            "  Nota: El login web usa CORREO. Las tablas usuario/rol del SQL "
            "legacy no se usan en este módulo."
        )
