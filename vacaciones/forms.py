from django import forms
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