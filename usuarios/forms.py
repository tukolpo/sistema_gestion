# usuarios/forms.py
# Integrante 1: Subtarea 1.2 — Validaciones en el Frontend (formularios Django + JS)
from django import forms
from django.contrib.auth.forms import AuthenticationForm
import re


class LoginForm(AuthenticationForm):
    """
    Formulario de inicio de sesión personalizado.
    Aplica validaciones de frontend: formato de correo, longitud mínima de contraseña.
    """
    error_messages = {
        'invalid_login': 'Credenciales incorrectas. Verifica tu correo y contraseña.',
        'inactive': 'Esta cuenta está inactiva.',
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
