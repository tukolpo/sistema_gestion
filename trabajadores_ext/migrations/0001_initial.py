from django.db import migrations, models
import django.db.models.deletion
import uuid
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("trabajadores", "0002_modelo_completo_y_documentos"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TrabajadorTokenQR",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ("activo", models.BooleanField(default=True)),
                ("generado_en", models.DateTimeField(auto_now_add=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                (
                    "trabajador",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="token_qr",
                        to="trabajadores.trabajador",
                    ),
                ),
            ],
            options={
                "verbose_name": "Token QR de trabajador",
                "verbose_name_plural": "Tokens QR de trabajadores",
            },
        ),
        migrations.CreateModel(
            name="EscaneoQR",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ip", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True, default="")),
                ("escaneado_en", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "token_qr",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="escaneos",
                        to="trabajadores_ext.trabajadortokenqr",
                    ),
                ),
            ],
            options={
                "verbose_name": "Escaneo QR",
                "verbose_name_plural": "Escaneos QR",
                "ordering": ["-escaneado_en"],
            },
        ),
        migrations.CreateModel(
            name="AuditoriaTrabajador",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "accion",
                    models.CharField(
                        choices=[
                            ("CREAR", "Crear"),
                            ("ACTUALIZAR", "Actualizar"),
                            ("ELIMINAR", "Eliminar"),
                            ("ESTADO", "Cambio de estado"),
                            ("DOCUMENTO", "Documento"),
                            ("QR_GENERADO", "QR generado"),
                            ("QR_ESCANEADO", "QR escaneado"),
                            ("ACCESO", "Acceso"),
                        ],
                        db_index=True,
                        max_length=20,
                    ),
                ),
                ("tabla", models.CharField(blank=True, default="", max_length=80)),
                ("registro_id", models.PositiveIntegerField(blank=True, null=True)),
                ("valor_anterior", models.TextField(blank=True, default="")),
                ("valor_nuevo", models.TextField(blank=True, default="")),
                ("ip", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True, default="")),
                ("ruta", models.CharField(blank=True, default="", max_length=255)),
                ("creado_en", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "trabajador",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="auditorias",
                        to="trabajadores.trabajador",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="auditorias_trabajadores",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Auditoría de trabajador",
                "verbose_name_plural": "Auditorías de trabajadores",
                "ordering": ["-creado_en"],
                "indexes": [
                    models.Index(fields=["-creado_en", "accion"], name="trabajador_ext_aud_idx"),
                    models.Index(fields=["tabla", "registro_id"], name="trabajador_ext_tab_idx"),
                ],
            },
        ),
    ]
