from django import forms
from .models import ConfiguracionGlobal


class ConfiguracionGlobalForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionGlobal
        fields = [
            "nombre_sistema",
            "tiempo_sesion_minutos",
            "dias_vacaciones_por_anio",
            "max_intentos_login",
            "minutos_bloqueo_login",
            "modo_mantenimiento",
        ]
        widgets = {
            "nombre_sistema": forms.TextInput(attrs={"class": "form-input"}),
            "tiempo_sesion_minutos": forms.NumberInput(attrs={"class": "form-input"}),
            "dias_vacaciones_por_anio": forms.NumberInput(attrs={"class": "form-input"}),
            "max_intentos_login": forms.NumberInput(attrs={"class": "form-input"}),
            "minutos_bloqueo_login": forms.NumberInput(attrs={"class": "form-input"}),
            "modo_mantenimiento": forms.CheckboxInput(),
        }