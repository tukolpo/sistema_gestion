from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from datetime import date

from trabajadores.models import Trabajador
from .models import SolicitudVacaciones


class SolicitudVacacionesForm(forms.ModelForm):
    class Meta:
        model = SolicitudVacaciones
        fields = ["trabajador", "fecha_inicio", "fecha_fin"]
        widgets = {
            "trabajador": forms.Select(attrs={"class": "form-input"}),
            "fecha_inicio": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
        }

    def clean(self):
        """Validaciones adicionales para la solicitud de vacaciones.

        Tarea 7 - Validar Sin Solapamiento:
        - Buscamos otras solicitudes del mismo trabajador cuyo estado sea
          PENDIENTE o APROBADA y cuyos rangos de fecha se crucen con el
          rango enviado. La condición de solapamiento en base de datos se
          evalúa con: existing.fecha_inicio <= nuevo.fecha_fin AND
          existing.fecha_fin >= nuevo.fecha_inicio.

        Tarea 8 - Validar Días Disponibles:
        - Calculamos los días solicitados usando objetos timedelta: se usa
          (fecha_fin - fecha_inicio).days + 1 para contar ambas fechas
          inclusive.
        - Para los días disponibles asumimos una política simple basada en
          15 días por año de antigüedad. Aquí se intenta llamar a una
          función externa `get_dias_vacaciones_disponibles(trabajador, fecha)`
          si existe; si no, se aplica un cálculo básico basado en años de
          servicio y restando los días ya aprobados en el mismo año.
        """

        cleaned = super().clean()
        trabajador = cleaned.get("trabajador")
        fecha_inicio = cleaned.get("fecha_inicio")
        fecha_fin = cleaned.get("fecha_fin")

        # Sólo validar si los tres campos están presentes
        if not (trabajador and fecha_inicio and fecha_fin):
            return cleaned

        # Aseguramos orden de fechas
        if fecha_fin < fecha_inicio:
            raise ValidationError("La fecha de fin debe ser igual o posterior a la fecha de inicio.")

        # -------------------------
        # Tarea 7: Validar Solapamiento
        # -------------------------
        # Consulta optimizada usando Q: buscamos solicitudes PENDIENTE o APROBADA
        estados_validos = [SolicitudVacaciones.Estado.PENDIENTE, SolicitudVacaciones.Estado.APROBADA]

        overlap_q = Q(fecha_inicio__lte=fecha_fin) & Q(fecha_fin__gte=fecha_inicio)
        estado_q = Q(estado__in=estados_validos)

        qs = SolicitudVacaciones.objects.filter(Q(trabajador=trabajador) & estado_q & overlap_q)

        # Si estamos editando una solicitud existente, excluirla de la comprobación
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            # Mensaje requerido por especificación
            raise ValidationError("Ya tienes una solicitud en ese período")

        # -------------------------
        # Tarea 8: Validar Días Disponibles
        # -------------------------
        # Días solicitados: usamos timedelta y contamos ambas fechas inclusive
        delta = fecha_fin - fecha_inicio
        dias_solicitados = max(delta.days + 1, 1)

        # Intentamos delegar el cálculo de días disponibles a una función externa
        # llamada `get_dias_vacaciones_disponibles(trabajador, fecha_referencia)`.
        # Si no existe, aplicamos una lógica básica:
        # - 15 días por año de antigüedad (años completos desde fecha_ingreso hasta fecha_inicio)
        # - restamos los días ya aprobados en el mismo año calendario
        dias_disponibles = None

        # Si el trabajador tiene un método auxiliar, úsalo
        get_dias_fn = getattr(trabajador, "get_dias_vacaciones_disponibles", None)
        if callable(get_dias_fn):
            dias_disponibles = get_dias_fn(fecha_inicio)
        else:
            # Try to import a standalone helper (may not exist in codebase)
            try:
                from .utils import get_dias_vacaciones_disponibles as helper_get_dias

                dias_disponibles = helper_get_dias(trabajador, fecha_inicio)
            except Exception:
                dias_disponibles = None

        # Fallback simple calculation when no helper is available
        if dias_disponibles is None:
            if not trabajador.fecha_ingreso:
                raise ValidationError("No se puede calcular días disponibles: trabajador sin fecha de ingreso.")

            # Calcular años completos de servicio hasta la fecha de inicio
            years = fecha_inicio.year - trabajador.fecha_ingreso.year
            # Ajuste si no ha cumplido aniversario en el año de referencia
            if (fecha_inicio.month, fecha_inicio.day) < (trabajador.fecha_ingreso.month or 1, trabajador.fecha_ingreso.day or 1):
                years -= 1
            years = max(years, 0)

            # Política simple: 15 días por año completo (mínimo 15 si tiene al menos 1 año)
            dias_entitlement = max(15 * max(years, 1), 15)

            # Restar días ya usados en el mismo año calendario (sólo solicitudes aprobadas)
            año = fecha_inicio.year
            usados_qs = SolicitudVacaciones.objects.filter(
                trabajador=trabajador,
                estado=SolicitudVacaciones.Estado.APROBADA,
                fecha_inicio__year=año,
            )
            usados = usados_qs.aggregate(total=Sum("dias_calculados"))
            dias_usados = usados.get("total") or 0

            dias_disponibles = max(dias_entitlement - dias_usados, 0)

        # Validación final: comparar solicitados vs disponibles
        if dias_solicitados > dias_disponibles:
            raise ValidationError(
                f"Días solicitados ({dias_solicitados}) superan los días disponibles ({dias_disponibles})."
            )

        # Guardar el cálculo en cleaned_data por si se necesita posteriormente
        cleaned["dias_solicitados"] = dias_solicitados
        cleaned["dias_disponibles"] = dias_disponibles

        return cleaned