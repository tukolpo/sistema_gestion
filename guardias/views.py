import json
from datetime import date

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from usuarios.constants import NIVEL_SUPERVISOR

from guardias.models import GuardiaTurno
from guardias.services import trabajador_del_usuario


@login_required
def gestion_guardias(request):
    """
    Supervisores y administradores: pantalla completa de gestión
    (Personal Disponible, Asignar Turno, Cronograma con navegación por semanas).

    Cualquier otro usuario (funcionario): solo puede ver, en modo lectura,
    el mini calendario con las guardias que se le asignaron a él.
    """
    es_supervisor = request.user.tiene_rango_minimo(NIVEL_SUPERVISOR)

    if not es_supervisor:
        trabajador_propio = trabajador_del_usuario(request.user)
        hoy = date.today()
        context = {
            "api_mis_guardias_url": "/api/guardias/mis-guardias/",
            "trabajador_propio": trabajador_propio,
            "sin_trabajador": trabajador_propio is None,
            "anio_actual": hoy.year,
            "mes_actual": hoy.month,
        }
        return render(request, "guardias/mis_guardias.html", context)

    turnos = GuardiaTurno.TurnoOpcion.choices  # [("MANANA", "Mañana"), ...]

    context = {
        "api_disponibilidad_url": "/api/guardias/disponibilidad/",
        "api_asignar_url": "/api/guardias/asignar/",
        "api_cronograma_url": "/api/guardias/cronograma/",
        "api_reporte_url": "/api/guardias/reporte/",
        "turnos": turnos,
        "turnos_json": json.dumps(turnos),
    }
    return render(request, "guardias/gestion_guardias.html", context)