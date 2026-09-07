from datetime import date

from trabajadores.models import Trabajador

from guardias.models import PermisoLaboral, VacacionSolicitud


class EstadoDisponibilidad:
    DISPONIBLE = "DISPONIBLE"
    INACTIVO = "INACTIVO"
    VACACIONES = "VACACIONES"
    PERMISO = "PERMISO"

    DISPLAY = {
        DISPONIBLE: "Disponible",
        INACTIVO: "Inactivo",
        VACACIONES: "Vacaciones",
        PERMISO: "Permiso",
    }


def consultar_disponibilidad(fecha=None):
    """Calcula la disponibilidad de cada funcionario para la fecha indicada."""
    fecha = fecha or date.today()

    trabajadores = Trabajador.objects.select_related("cargo").order_by(
        "apellido", "nombre"
    )

    en_vacaciones = set(
        VacacionSolicitud.objects.filter(
            estado=VacacionSolicitud.Estado.APROBADA,
            fecha_inicio__lte=fecha,
            fecha_fin__gte=fecha,
        ).values_list("trabajador_id", flat=True)
    )

    en_permiso = set(
        PermisoLaboral.objects.filter(
            estado=PermisoLaboral.Estado.APROBADO,
            fecha_inicio__lte=fecha,
            fecha_fin__gte=fecha,
        ).values_list("trabajador_id", flat=True)
    )

    resultados = []
    for trabajador in trabajadores:
        if trabajador.estado == Trabajador.Estado.INACTIVO:
            estado = EstadoDisponibilidad.INACTIVO
            disponible = False
            motivo = "Funcionario inactivo en el sistema"
        elif trabajador.id in en_vacaciones:
            estado = EstadoDisponibilidad.VACACIONES
            disponible = False
            motivo = "Vacaciones aprobadas"
        elif trabajador.id in en_permiso:
            estado = EstadoDisponibilidad.PERMISO
            disponible = False
            motivo = "Permiso laboral aprobado"
        else:
            estado = EstadoDisponibilidad.DISPONIBLE
            disponible = True
            motivo = None

        resultados.append(
            {
                "id": trabajador.id,
                "nombre": trabajador.nombre,
                "apellido": trabajador.apellido,
                "nombre_completo": str(trabajador),
                "cedula": trabajador.cedula,
                "cargo": trabajador.cargo.nombre if trabajador.cargo_id else None,
                "disponible": disponible,
                "estado_disponibilidad": estado,
                "estado_disponibilidad_display": EstadoDisponibilidad.DISPLAY[estado],
                "motivo": motivo,
            }
        )

    return resultados

from django.core.exceptions import ValidationError
from guardias.models import GuardiaTurno

def asignar_turno_funcionario(trabajador_id, fecha, turno):
    disponibilidades = consultar_disponibilidad(fecha)
    func_info = next((f for f in disponibilidades if f["id"] == int(trabajador_id)), None)
    
    if not func_info or not func_info["disponible"]:
        motivo = func_info["motivo"] if func_info else "No disponible"
        raise ValidationError(f"No se puede asignar el turno: el funcionario no está disponible ({motivo}).")

    turno_existente = GuardiaTurno.objects.filter(
        trabajador_id=trabajador_id,
        fecha=fecha
    ).exists()

    if turno_existente:
        raise ValidationError("El funcionario ya tiene un turno asignado para esta fecha.")

    return GuardiaTurno.objects.create(
        trabajador_id=trabajador_id,
        fecha=fecha,
        turno=turno
    )