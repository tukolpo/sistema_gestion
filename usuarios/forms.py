# usuarios/forms.py
# Integrante 1: Subtarea 1.2 — Validaciones en el Frontend (formularios Django + JS)
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
import re

from usuarios.constants import (
    MENSAJE_CREDENCIALES_INCORRECTAS,
    MENSAJE_CUENTA_BLOQUEADA,
)
from usuarios.security import (
    buscar_usuario_por_email,
    login_esta_bloqueado,
    registrar_login_fallido,
)


class LoginForm(AuthenticationForm):
    """
    Formulario de inicio de sesión personalizado.
    Aplica validaciones de frontend: formato de correo, longitud mínima de contraseña.
    """
    error_messages = {
        'invalid_login': MENSAJE_CREDENCIALES_INCORRECTAS,
        'inactive': MENSAJE_CREDENCIALES_INCORRECTAS,
    }

    username = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'id': 'id_email',
            'class': 'form-input',
            'placeholder': 'Correo Electrónico',
            'autocomplete': 'email',
            'aria-label': 'Correo electrónico',
        })
    )
    password = forms.CharField(
        label='Contraseña',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'id': 'id_password',
            'class': 'form-input',
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password',
            'aria-label': 'Contraseña',
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        label='Recordar contraseña',
        widget=forms.CheckboxInput(attrs={
            'id': 'id_remember_me',
            'class': 'form-checkbox',
        })
    )

    def clean_username(self):
        """Validación: el correo debe tener formato válido."""
        email = self.cleaned_data.get('username', '').strip()
        patron_email = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(patron_email, email):
            raise forms.ValidationError('Ingresa un correo electrónico válido.')
        return email

    def clean_password(self):
        """Validación: la contraseña debe tener al menos 8 caracteres."""
        password = self.cleaned_data.get('password', '')
        if len(password) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')
        return password

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            user = buscar_usuario_por_email(username)
            if login_esta_bloqueado(user, request=self.request):
                raise ValidationError(
                    MENSAJE_CUENTA_BLOQUEADA,
                    code="account_locked",
                )

        try:
            return super().clean()
        except ValidationError as exc:
            user = buscar_usuario_por_email(username or "")
            codes = {
                error.code for error in exc.error_list
            } if hasattr(exc, "error_list") else {exc.code}
            if codes & {"invalid_login", "inactive"}:
                registrar_login_fallido(self.request, user=user)
                if user and user.esta_bloqueado():
                    raise ValidationError(
                        MENSAJE_CUENTA_BLOQUEADA,
                        code="account_locked",
                    )
            raise

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.esta_bloqueado():
            raise ValidationError(
                MENSAJE_CUENTA_BLOQUEADA,
                code="account_locked",
            )


from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario

class UsuarioCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("username", "email", "first_name", "last_name", "cedula", "departamento", "rol")
        
    def clean_cedula(self):
        cedula = self.cleaned_data.get("cedula")
        if cedula == "":
            return None
        return cedula

class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = ("username", "email", "first_name", "last_name", "cedula", "departamento", "rol", "is_active")

    def clean_cedula(self):
        cedula = self.cleaned_data.get("cedula")
        if cedula == "":
            return None
        return cedula


class CambiarPasswordForm(forms.Form):
    password1 = forms.CharField(
        label="Nueva contraseña",
        min_length=8,
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "Mínimo 8 caracteres"})
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "Repite la contraseña"})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data


from .models import Rol

class RolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = ("nombre", "nivel_jerarquia", "descripcion")
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Ej: Gerente de RRHH"}),
            "nivel_jerarquia": forms.NumberInput(attrs={"placeholder": "0 - 100", "min": 0, "max": 100}),
            "descripcion": forms.Textarea(attrs={"rows": 3, "placeholder": "Descripción breve del rol..."}),
        }
        help_texts = {
            "nivel_jerarquia": "100 = Administrador, 50 = Gerente, 40 = Supervisor, 20 = Trabajador, 10 = Funcionario",
        }
