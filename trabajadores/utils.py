
from datetime import date
from dateutil.relativedelta import relativedelta
from trabajadores.models import Trabajador


def cambiar_estado_trabajador(trabajador, nuevo_estado=None):
    """
    Cambia el estado del trabajador.
    Si nuevo_estado es None, alterna entre ACTIVO e INACTIVO.
    """
    if nuevo_estado is not None:
        if nuevo_estado not in Trabajador.Estado.values:
            raise ValueError("Estado no válido.")
        trabajador.estado = nuevo_estado
        trabajador.save(update_fields=["estado", "fecha_actualizacion"])
    else:
        trabajador.alternar_estado()
    return trabajador

def obtener_umbrales_antiguedad():
    hoy = date.today()
    return {
        'hace_1_ano': hoy - relativedelta(years=1),
        'hace_5_anos': hoy - relativedelta(years=5),
        'hace_10_anos': hoy - relativedelta(years=10),
    }


def trabajador_del_usuario(usuario):
    """Trabajador cuyo correo coincide con el de la cuenta (sin distinguir mayúsculas).
    Mismo criterio que usan las apps de vacaciones y guardias para vincular
    una cuenta de usuario con su ficha de trabajador."""
    correo = (usuario.email or "").strip()
    if not correo:
        return None
    return Trabajador.objects.filter(email__iexact=correo).first()