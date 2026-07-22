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
