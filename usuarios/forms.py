
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


from django.contrib.auth.password_validation import validate_password
from usuarios.models import Usuario, Rol


class CrearUsuarioForm(forms.Form):
    password_confirmacion_admin = forms.CharField(
        label="Tu contraseña (para confirmar esta acción)",
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
    )
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={"class": "form-input"}),
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
    )
    password2 = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
    )
    rol = forms.ModelChoiceField(
        label="Rol",
        queryset=Rol.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-input"}),
    )

    def __init__(self, *args, roles_disponibles=None, admin_user=None, **kwargs):
        # Capturamos el argumento personalizado antes de llamar a super() para evitar el TypeError
        self.admin_user = admin_user
        super().__init__(*args, **kwargs)
        if roles_disponibles is not None:
            self.fields["rol"].queryset = roles_disponibles

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise ValidationError("Ya existe un usuario con este correo.")
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("Las contraseñas no coinciden.")
        if p2:
            validate_password(p2)
        return p2

    def guardar(self):
        email = self.cleaned_data["email"]
        usuario = Usuario(username=email, email=email, rol=self.cleaned_data.get("rol"))
        usuario.set_password(self.cleaned_data["password1"])
        usuario.save()
        return usuario