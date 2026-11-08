# configuracion/forms.py
from django import forms

from .context_processors import TEMAS
from .models import ConfiguracionGlobal

# campo: (mínimo, máximo, unidad que se muestra dentro del campo)
LIMITES = {
    "tiempo_sesion_minutos": (5, 480, "min"),
    "max_intentos_login": (3, 10, "intentos"),
    "minutos_bloqueo_login": (1, 1440, "min"),
}


def _widget_numerico(campo):
    minimo, maximo, unidad = LIMITES[campo]
    return forms.NumberInput(
        attrs={
            "class": "form-input",
            "min": minimo,
            "max": maximo,
            "step": 1,
            "inputmode": "numeric",
            "data_unidad": unidad,
        }
    )


class ConfiguracionGlobalForm(forms.ModelForm):
    tema = forms.ChoiceField(
        label="Color del sistema",
        choices=[(clave, datos[0]) for clave, datos in TEMAS.items()],
        widget=forms.RadioSelect,
    )

    class Meta:
        model = ConfiguracionGlobal
        fields = [
            "tiempo_sesion_minutos",
            "max_intentos_login",
            "minutos_bloqueo_login",
            "modo_mantenimiento",
            "tema",
        ]
        labels = {
            "tiempo_sesion_minutos": "Tiempo de sesión",
            "max_intentos_login": "Intentos máximos de login",
            "minutos_bloqueo_login": "Minutos de bloqueo",
            "modo_mantenimiento": "Modo mantenimiento",
        }
        help_texts = {
            "tiempo_sesion_minutos": "Tiempo máximo de inactividad antes de cerrar la sesión.",
            "max_intentos_login": "Intentos fallidos permitidos antes de bloquear la cuenta.",
            "minutos_bloqueo_login": "Cuánto dura el bloqueo tras superar los intentos.",
            "modo_mantenimiento": (
                "Si está activo, solo los administradores (nivel jerárquico 100) "
                "pueden usar el sistema. El resto de usuarios será cerrado y "
                "redirigido al inicio de sesión."
            ),
        }
        widgets = {
            "tiempo_sesion_minutos": _widget_numerico("tiempo_sesion_minutos"),
            "max_intentos_login": _widget_numerico("max_intentos_login"),
            "minutos_bloqueo_login": _widget_numerico("minutos_bloqueo_login"),
            "modo_mantenimiento": forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Los validadores del modelo añaden min/max al widget y pisarían estos
        # límites (de ahí el "Entre 0 y ..."); se fijan después de construir el form.
        for campo, (minimo, maximo, _unidad) in LIMITES.items():
            self.fields[campo].widget.attrs.update(min=minimo, max=maximo)

        # Datos de las muestras de color para la plantilla.
        self.temas_info = [
            {"valor": clave, "nombre": d[0], "base": d[1], "oscuro": d[2],
             "claro": d[3], "fondo": d[4], "fondo_claro": d[5]}
            for clave, d in TEMAS.items()
        ]

    def clean(self):
        datos = super().clean()
        for campo, (minimo, maximo, _unidad) in LIMITES.items():
            valor = datos.get(campo)
            if valor is None:
                continue
            if valor < minimo or valor > maximo:
                self.add_error(
                    campo, f"Debe estar entre {minimo} y {maximo}."
                )
        return datos