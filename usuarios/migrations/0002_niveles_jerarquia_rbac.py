"""Corrige niveles jerárquicos (1-4 → 100/50/10) para que RBAC funcione con las vistas."""

from django.db import migrations


def corregir_niveles(apps, schema_editor):
    Rol = apps.get_model("usuarios", "Rol")

    por_nombre = {
        "Administrador": 100,
        "Gerente de guardias": 50,
        "Supervisor": 40,
        "Trabajador": 20,
        "Funcionario": 10,
    }
    for nombre, nivel in por_nombre.items():
        Rol.objects.filter(nombre=nombre).update(nivel_jerarquia=nivel)

    # Datos antiguos importados con niveles 1, 2, 3, 4
    legacy_map = {1: 100, 2: 50, 3: 20, 4: 10}
    for antiguo, nuevo in legacy_map.items():
        Rol.objects.filter(nivel_jerarquia=antiguo).update(nivel_jerarquia=nuevo)


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(corregir_niveles, migrations.RunPython.noop),
    ]
