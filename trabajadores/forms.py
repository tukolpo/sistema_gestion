from django import forms

from trabajadores.models import DocumentoTrabajador, Trabajador
from trabajadores.validators import validar_archivo_documento, validar_archivo_foto


class TrabajadorForm(forms.ModelForm):
    class Meta:
        model = Trabajador
        fields = [
            "nombre",
            "apellido",
            "cedula",
            "fecha_nacimiento",
            "fecha_ingreso",
            "cargo",
            "especialidad",
            "estado",
            "telefono",
            "email",
            "notas_perfil",
            "foto",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-input"}),
            "apellido": forms.TextInput(attrs={"class": "form-input"}),
            "cedula": forms.TextInput(attrs={"class": "form-input"}),
            "cargo": forms.Select(attrs={"class": "form-input"}),
            "especialidad": forms.Select(attrs={"class": "form-input"}),
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
