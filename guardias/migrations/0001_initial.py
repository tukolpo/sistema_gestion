import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("trabajadores", "0002_modelo_completo_y_documentos"),
    ]

    operations = [
        migrations.CreateModel(
            name="VacacionSolicitud",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fecha_solicitud", models.DateField(auto_now_add=True)),
                ("fecha_inicio", models.DateField()),
                ("fecha_fin", models.DateField()),
                (
                    "dias_solicitados",
                    models.PositiveSmallIntegerField(blank=True, null=True),
                ),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("PENDIENTE", "Pendiente"),
                            ("APROBADA", "Aprobada"),
                            ("RECHAZADA", "Rechazada"),
                        ],
                        db_index=True,
                        default="PENDIENTE",
                        max_length=10,
                    ),
                ),
                (
                    "trabajador",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vacaciones",
                        to="trabajadores.trabajador",
                    ),
                ),
            ],
            options={
                "verbose_name": "Solicitud de vacaciones",
                "verbose_name_plural": "Solicitudes de vacaciones",
                "ordering": ["-fecha_inicio"],
            },
        ),
        migrations.CreateModel(
            name="PermisoLaboral",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fecha_inicio", models.DateField()),
                ("fecha_fin", models.DateField()),
                ("motivo", models.CharField(blank=True, max_length=200)),
                (
                    "estado",
                    models.CharField(
                        choices=[
                            ("PENDIENTE", "Pendiente"),
                            ("APROBADO", "Aprobado"),
                            ("RECHAZADO", "Rechazado"),
                        ],
                        db_index=True,
                        default="PENDIENTE",
                        max_length=10,
                    ),
                ),
                (
                    "trabajador",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="permisos_laborales",
                        to="trabajadores.trabajador",
                    ),
                ),
            ],
            options={
                "verbose_name": "Permiso laboral",
                "verbose_name_plural": "Permisos laborales",
                "ordering": ["-fecha_inicio"],
            },
        ),
    ]
