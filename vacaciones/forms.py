from django import forms

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

    def clean(self):
        cleaned = super().clean()
        trabajador = cleaned.get("trabajador")
        inicio = cleaned.get("fecha_inicio")
        fin = cleaned.get("fecha_fin")

        if not (trabajador and inicio and fin):
            return cleaned

        if fin < inicio:
            self.add_error("fecha_fin", "La fecha de fin no puede ser anterior a la de inicio.")
            return cleaned

        dias_solicitados = (fin - inicio).days + 1
        dias_disponibles = calcular_dias_disponibles(trabajador)["dias_disponibles"]

        if dias_solicitados > dias_disponibles:
            raise forms.ValidationError(
                f"{trabajador} solicita {dias_solicitados} días, "
                f"pero solo tiene {dias_disponibles} disponibles."
            )

        return cleaned