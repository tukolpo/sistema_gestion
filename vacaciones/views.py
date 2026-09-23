import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from usuarios.decorators import requiere_jerarquia
from usuarios.constants import NIVEL_SUPERVISOR

from trabajadores.models import Trabajador

from .forms import SolicitudVacacionesForm
from .models import SolicitudVacaciones
from .services import calcular_dias_disponibles


def _trabajador_del_usuario(usuario):
    """Trabajador cuyo correo coincide con el de la cuenta (sin distinguir mayúsculas)."""
    correo = (usuario.email or "").strip()
    if not correo:
        return None
    return Trabajador.objects.filter(email__iexact=correo).first()


@login_required
def crear_solicitud(request):
    es_supervisor = request.user.tiene_rango_minimo(NIVEL_SUPERVISOR)

    # Supervisores y administradores eligen a cualquier trabajador.
    # Los demás usuarios solo pueden pedir vacaciones para sí mismos.
    trabajador_propio = None if es_supervisor else _trabajador_del_usuario(request.user)
    sin_trabajador = (not es_supervisor) and trabajador_propio is None

    datos = None
    if request.method == "POST":
        if sin_trabajador:
            messages.error(
                request,
                "Tu cuenta no está vinculada a ningún trabajador; no puedes solicitar vacaciones.",
            )
            return redirect("vacaciones:gestion_vacaciones")
        datos = request.POST.copy()
        if trabajador_propio:
            # Se ignora lo que envíe el navegador: siempre es el trabajador de la cuenta
            datos["trabajador"] = trabajador_propio.pk

    form = SolicitudVacacionesForm(datos)
    if trabajador_propio:
        form.fields["trabajador"].queryset = Trabajador.objects.filter(pk=trabajador_propio.pk)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Solicitud de vacaciones enviada correctamente.")
        return redirect("vacaciones:gestion_vacaciones")

    if es_supervisor:
        trabajadores_con_dias = [
            {"trabajador": t, **calcular_dias_disponibles(t)}
            for t in Trabajador.objects.all()
        ]
        dias_por_trabajador = {
            item["trabajador"].id: item["dias_disponibles"]
            for item in trabajadores_con_dias
        }
    else:
        # El funcionario solo recibe los días de su propio trabajador
        trabajadores_con_dias = []
        dias_por_trabajador = {}
        if trabajador_propio:
            dias_por_trabajador = {
                trabajador_propio.id: calcular_dias_disponibles(trabajador_propio)["dias_disponibles"]
            }

    return render(request, "vacaciones/gestion_vacaciones.html", {
        "form": form,
        "trabajadores_con_dias": trabajadores_con_dias,
        "dias_disponibles_json": json.dumps(dias_por_trabajador),
        "es_supervisor": es_supervisor,
        "trabajador_propio": trabajador_propio,
        "sin_trabajador": sin_trabajador,
    })


@login_required
def gestion_vacaciones(request):
    """Pantalla principal de vacaciones: es la misma de crear_solicitud."""
    return crear_solicitud(request)


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_SUPERVISOR)
def lista_solicitudes(request):
    solicitudes = SolicitudVacaciones.objects.select_related("trabajador").order_by("-fecha_creacion")

    return render(request, "vacaciones/lista_solicitudes.html", {
        "solicitudes": solicitudes,
    })


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_SUPERVISOR)
@require_POST
def cambiar_estado_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudVacaciones, id=solicitud_id)
    nuevo_estado = request.POST.get("estado")
    Estado = SolicitudVacaciones.Estado

    if nuevo_estado not in (Estado.APROBADA, Estado.RECHAZADA):
        messages.error(request, "Estado no válido.")
    elif solicitud.estado != Estado.PENDIENTE:
        messages.error(
            request,
            f"La solicitud ya fue {solicitud.get_estado_display().lower()}; no se puede cambiar.",
        )
    elif nuevo_estado == Estado.APROBADA:
        disponibles = calcular_dias_disponibles(solicitud.trabajador)["dias_disponibles"]
        if solicitud.dias_calculados > disponibles:
            messages.error(
                request,
                f"No se puede aprobar: {solicitud.trabajador} solicita "
                f"{solicitud.dias_calculados} días y solo tiene {disponibles} disponibles.",
            )
        else:
            solicitud.estado = nuevo_estado
            solicitud.save(update_fields=["estado"])
            messages.success(request, f"Solicitud de {solicitud.trabajador} aprobada.")
    else:
        solicitud.estado = nuevo_estado
        solicitud.save(update_fields=["estado"])
        messages.success(request, f"Solicitud de {solicitud.trabajador} rechazada.")

    return redirect("vacaciones:lista_solicitudes")