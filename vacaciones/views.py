from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from trabajadores.models import Trabajador

from .forms import SolicitudVacacionesForm
from .services import calcular_dias_disponibles


@login_required
def gestion_vacaciones(request):
    if request.method == "POST":
        form = SolicitudVacacionesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("vacaciones:gestion_vacaciones")
    else:
        form = SolicitudVacacionesForm()

    trabajadores_con_dias = [
        {"trabajador": t, **calcular_dias_disponibles(t)}
        for t in Trabajador.objects.all()
    ]

    return render(request, "vacaciones/gestion_vacaciones.html", {
        "form": form,
        "trabajadores_con_dias": trabajadores_con_dias,
    })