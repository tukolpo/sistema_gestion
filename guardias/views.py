from django.shortcuts import render

def gestion_guardias(request):
    # Datos de ejemplo — en la Tarea 2 esto se reemplaza por consulta real
    disponibles = [
        {"nombre": "Daniel Torres"},
        {"nombre": "Valery Gonzalez"},
        {"nombre": "Saul Ramirez"},
        {"nombre": "Jostin Oropeza"},
    ]
    turnos = ["Mañana", "Tarde", "Noche"]
    dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

    context = {
        "disponibles": disponibles,
        "turnos": turnos,
        "dias": dias,
        "seccion_activa": "guardias",
    }
    return render(request, "guardias/gestion_guardias.html", context)