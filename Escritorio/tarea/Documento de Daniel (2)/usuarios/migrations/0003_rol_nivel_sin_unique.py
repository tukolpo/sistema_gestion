from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0002_niveles_jerarquia_rbac"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rol",
            name="nivel_jerarquia",
            field=models.IntegerField(
                help_text="100=Admin, 50=Gerente, 40=Supervisor, 20=Trabajador, 10=Funcionario",
            ),
        ),
    ]
