from datetime import date

from django import forms

from trabajadores.antiguedad import MAYORIA_DE_EDAD, es_mayor_de_edad, fecha_limite_mayoria
from trabajadores.models import DocumentoTrabajador, Trabajador
from trabajadores.validators import (
    normalizar_cedula,
    validar_archivo_documento,
    validar_archivo_foto,
    validar_cedula_venezuela,
)


class TrabajadorForm(forms.ModelForm):
    class Meta:
        model = Trabajador
        fields = [
            "nombre",
            "apellido",
            "cedula",
            "fecha_nacimiento",
            "fecha_ingreso",
            "estado",
            "telefono",
            "email",
            "notas_perfil",
            "foto",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-input"}),
            "apellido": forms.TextInput(attrs={"class": "form-input"}),
            "cedula": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "V-12345678",
                    "maxlength": "10",
                }
            ),
            "estado": forms.Select(attrs={"class": "form-input"}),
            "telefono": forms.TextInput(attrs={"class": "form-input"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
            "notas_perfil": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "fecha_nacimiento": forms.DateInput(
                attrs={"class": "form-input", "type": "date"}
            ),
            "fecha_ingreso": forms.DateInput(
                attrs={"class": "form-input", "type": "date"}
            ),
            "foto": forms.FileInput(attrs={"class": "form-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obligatorios al registrar o editar un trabajador.
        self.fields["fecha_nacimiento"].required = True
        self.fields["fecha_nacimiento"].error_messages["required"] = (
            "La fecha de nacimiento es obligatoria."
        )
        self.fields["telefono"].required = True
        self.fields["telefono"].error_messages["required"] = (
            "El teléfono es obligatorio."
        )
        self.fields["email"].required = True
        self.fields["email"].error_messages["required"] = (
            "El correo electrónico es obligatorio."
        )
        # La fecha de ingreso es obligatoria al registrar o editar un trabajador.
        self.fields["fecha_ingreso"].required = True
        self.fields["fecha_ingreso"].error_messages["required"] = (
            "La fecha de ingreso es obligatoria."
        )
        self.fields["fecha_ingreso"].widget.attrs["max"] = date.today().isoformat()
        # Solo mayores de edad: el selector no deja elegir fechas posteriores.
        self.fields["fecha_nacimiento"].widget.attrs["max"] = fecha_limite_mayoria().isoformat()

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get("fecha_nacimiento")
        if fecha and not es_mayor_de_edad(fecha):
            raise forms.ValidationError(
                f"El trabajador debe ser mayor de {MAYORIA_DE_EDAD} años."
            )
        return fecha

    def clean_telefono(self):
        telefono = (self.cleaned_data.get("telefono") or "").strip()
        if not telefono:
            raise forms.ValidationError("El teléfono es obligatorio.")
        return telefono

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if not email:
            raise forms.ValidationError("El correo electrónico es obligatorio.")
        return email

    def clean_fecha_ingreso(self):
        fecha = self.cleaned_data.get("fecha_ingreso")
        if fecha and fecha > date.today():
            raise forms.ValidationError("La fecha de ingreso no puede ser futura.")
        return fecha

    def clean_cedula(self):
        valor = normalizar_cedula(self.cleaned_data.get("cedula"))
        validar_cedula_venezuela(valor)

        # Evita choque con otro trabajador que ya tenga esa cédula normalizada
        qs = Trabajador.objects.filter(cedula=valor)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un trabajador con esta cédula.")

        return valor

    def clean_foto(self):
        foto = self.cleaned_data.get("foto")
        validar_archivo_foto(foto)
        return foto


class DocumentoTrabajadorForm(forms.ModelForm):
    class Meta:
        model = DocumentoTrabajador
        fields = ["tipo", "titulo", "archivo"]
        widgets = {
            "tipo": forms.Select(attrs={"class": "form-input"}),
            "titulo": forms.TextInput(attrs={"class": "form-input"}),
            "archivo": forms.FileInput(attrs={"class": "form-input"}),
        }

    def clean_archivo(self):
        archivo = self.cleaned_data.get("archivo")
        validar_archivo_documento(archivo)
        return archivo