from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from datetime import date

from .models import SolicitudVacaciones
from .services import calcular_dias_disponibles


class SolicitudVacacionesForm(forms.ModelForm):
    class Meta:
        model = SolicitudVacaciones
        fields = ["trabajador", "fecha_inicio", "fecha_fin"]
        widgets = {
            "trabajador": forms.Select(attrs={"class": "form-input"}),
            "fecha_inicio": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "fecha_fin": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
        }

    def clean_fecha_inicio(self):
       
        fecha_inicio = self.cleaned_data.get("fecha_inicio")
        if fecha_inicio and fecha_inicio < date.today():
            raise ValidationError("La fecha de inicio no puede ser en el pasado")
        return fecha_inicio

    def clean(self):
        cleaned = super().clean()
        trabajador = cleaned.get("trabajador")
        fecha_inicio = cleaned.get("fecha_inicio")
        fecha_fin = cleaned.get("fecha_fin")

        if not (trabajador and fecha_inicio and fecha_fin):
            return cleaned

      
        if fecha_fin <= fecha_inicio:
            raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio")

        
        estados_validos = [SolicitudVacaciones.Estado.PENDIENTE, SolicitudVacaciones.Estado.APROBADA]
        overlap_q = Q(fecha_inicio__lte=fecha_fin) & Q(fecha_fin__gte=fecha_inicio)
        estado_q = Q(estado__in=estados_validos)

        qs = SolicitudVacaciones.objects.filter(Q(trabajador=trabajador) & estado_q & overlap_q)

        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError("Ya tienes una solicitud en ese período")

        
        dias_solicitados = (fecha_fin - fecha_inicio).days + 1
        dias_disponibles = calcular_dias_disponibles(trabajador)["dias_disponibles"]

        if dias_solicitados > dias_disponibles:
            raise ValidationError(
                f"{trabajador} solicita {dias_solicitados} días, "
                f"pero solo tiene {dias_disponibles} disponibles."
            )

        return cleaned