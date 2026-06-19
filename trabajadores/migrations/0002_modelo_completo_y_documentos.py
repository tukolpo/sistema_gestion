import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import trabajadores.models
import trabajadores.storage


def _sembrar_catalogos(apps):
    Cargo = apps.get_model("trabajadores", "Cargo")
    Especialidad = apps.get_model("trabajadores", "Especialidad")
    for nombre in ("General", "Administrativo", "Operativo", "Supervisor"):
        Cargo.objects.get_or_create(nombre=nombre)
    for nombre in ("Ninguna", "Seguridad", "Recursos Humanos", "Logística"):
        Especialidad.objects.get_or_create(nombre=nombre)


def migrar_cargos_y_estados(apps, schema_editor):
    Trabajador = apps.get_model("trabajadores", "Trabajador")
    Cargo = apps.get_model("trabajadores", "Cargo")
    Especialidad = apps.get_model("trabajadores", "Especialidad")

    if not Trabajador.objects.exists():
        Cargo.objects.get_or_create(
            nombre="General", defaults={"descripcion": "Cargo por defecto"}
        )
        return

    for nombre in (
        Trabajador.objects.values_list("cargo", flat=True).distinct()
    ):
        if nombre:
            Cargo.objects.get_or_create(nombre=nombre)

    cargo_default = Cargo.objects.filter(nombre="General").first()
    if cargo_default is None:
        cargo_default = Cargo.objects.create(nombre="General")

    for trabajador in Trabajador.objects.all():
        cargo_obj = (
            Cargo.objects.filter(nombre=trabajador.cargo).first() or cargo_default
        )
        esp = None
        if trabajador.especialidad:
            esp, _ = Especialidad.objects.get_or_create(
                nombre=trabajador.especialidad
            )
        trabajador.cargo_fk = cargo_obj
        trabajador.especialidad_fk = esp
        trabajador.estado = (
            "ACTIVO" if trabajador.activo else "INACTIVO"
        )
        trabajador.save(
            update_fields=["cargo_fk", "especialidad_fk", "estado"]
        )


class Migration(migrations.Migration):

    dependencies = [
        ("trabajadores", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Cargo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=100, unique=True)),
                ("descripcion", models.TextField(blank=True)),
            ],
            options={
                "verbose_name": "Cargo",
                "verbose_name_plural": "Cargos",
                "ordering": ["nombre"],
            },
        ),
        migrations.CreateModel(
            name="Especialidad",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=100, unique=True)),
                ("descripcion", models.TextField(blank=True)),
            ],
            options={
                "verbose_name": "Especialidad",
                "verbose_name_plural": "Especialidades",
                "ordering": ["nombre"],
            },
        ),
        migrations.AddField(
            model_name="trabajador",
            name="cargo_fk",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="trabajadores",
                to="trabajadores.cargo",
            ),
        ),
        migrations.AddField(
            model_name="trabajador",
            name="especialidad_fk",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="trabajadores",
                to="trabajadores.especialidad",
            ),
        ),
        migrations.AddField(
            model_name="trabajador",
            name="estado",
            field=models.CharField(
                choices=[("ACTIVO", "Activo"), ("INACTIVO", "Inactivo")],
                db_index=True,
                default="ACTIVO",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="trabajador",
            name="telefono",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="trabajador",
            name="email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="trabajador",
            name="notas_perfil",
            field=models.TextField(blank=True, verbose_name="Notas del perfil"),
        ),
        migrations.AddField(
            model_name="trabajador",
            name="fecha_actualizacion",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.RunPython(migrar_cargos_y_estados, migrations.RunPython.noop),
        migrations.RemoveField(model_name="trabajador", name="cargo"),
        migrations.RemoveField(model_name="trabajador", name="especialidad"),
        migrations.RemoveField(model_name="trabajador", name="activo"),
        migrations.RenameField(
            model_name="trabajador",
            old_name="cargo_fk",
            new_name="cargo",
        ),
        migrations.RenameField(
            model_name="trabajador",
            old_name="especialidad_fk",
            new_name="especialidad",
        ),
        migrations.AlterField(
            model_name="trabajador",
            name="cargo",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="trabajadores",
                to="trabajadores.cargo",
            ),
        ),
        migrations.AlterField(
            model_name="trabajador",
            name="foto",
            field=models.ImageField(
                blank=True,
                null=True,
                storage=trabajadores.storage.private_storage,
                upload_to=trabajadores.models._ruta_foto,
            ),
        ),
        migrations.RunPython(
            lambda apps, schema_editor: _sembrar_catalogos(apps),
            migrations.RunPython.noop,
        ),
        migrations.CreateModel(
            name="DocumentoTrabajador",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("CEDULA", "Cédula"),
                            ("CONTRATO", "Contrato"),
                            ("CERTIFICADO", "Certificado"),
                            ("OTRO", "Otro"),
                        ],
                        default="OTRO",
                        max_length=20,
                    ),
                ),
                ("titulo", models.CharField(max_length=150)),
                (
                    "archivo",
                    models.FileField(
                        storage=trabajadores.storage.private_storage,
                        upload_to=trabajadores.models._ruta_documento,
                    ),
                ),
                ("subido_en", models.DateTimeField(auto_now_add=True)),
                (
                    "subido_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="documentos_trabajador_subidos",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "trabajador",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documentos",
                        to="trabajadores.trabajador",
                    ),
                ),
            ],
            options={
                "verbose_name": "Documento de trabajador",
                "verbose_name_plural": "Documentos de trabajadores",
                "ordering": ["-subido_en"],
            },
        ),
    ]
