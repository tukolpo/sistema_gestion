from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta

@login_required
def gestion_guardias(request):
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    dias = [(inicio_semana + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    context = {
        "api_disponibilidad_url": "/api/guardias/disponibilidad/",
        "api_asignar_url": "/api/guardias/asignar/",
        "api_cronograma_url": "/api/guardias/cronograma/",
        "api_reporte_url": "/api/guardias/reporte/",
        "turnos": ["MANANA", "TARDE", "NOCHE"],
        "dias": dias,
    }
    return render(request, "guardias/gestion_guardias.html", context)