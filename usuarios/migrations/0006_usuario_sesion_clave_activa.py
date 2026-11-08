from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0005_alter_securitylog_action"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuario",
            name="sesion_clave_activa",
            field=models.CharField(blank=True, default="", max_length=40),
        ),
    ]
