from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from usuarios.constants import NIVEL_GESTION_USUARIOS
from usuarios.decorators import requiere_jerarquia


@login_required
@requiere_jerarquia(NIVEL_GESTION_USUARIOS)
def gestion_guardias(request):
    turnos = ["Mañana", "Tarde", "Noche"]
    dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

    context = {
        "turnos": turnos,
        "dias": dias,
        "seccion_activa": "guardias",
        "api_disponibilidad_url": "/api/guardias/disponibilidad/",
    }
    return render(request, "guardias/gestion_guardias.html", context)
