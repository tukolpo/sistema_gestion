# usuarios/serializers.py
# Serializers JWT (API)

from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from usuarios.backends import EmailBackend
from usuarios.constants import (
    MENSAJE_CREDENCIALES_INCORRECTAS,
    MENSAJE_CUENTA_BLOQUEADA,
    MENSAJE_MANTENIMIENTO,
    NIVEL_ADMINISTRADOR,
)
from usuarios.security import (
    buscar_usuario_por_email,
    login_esta_bloqueado,
    registrar_login_exitoso,
    registrar_login_fallido,
)


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Acepta correo en el campo ``username`` del JSON (igual que el login web)."""

    def validate(self, attrs):
        identificador = (attrs.get("username") or "").strip()
        password = attrs.get("password")
        request = self.context.get("request")

        usuario = buscar_usuario_por_email(identificador)
        if login_esta_bloqueado(usuario, request=request):
            raise AuthenticationFailed(
                MENSAJE_CUENTA_BLOQUEADA,
                code="account_locked",
            )

        user = EmailBackend().authenticate(
            request=request,
            username=identificador,
            password=password,
        )
        if user is None:
            user = authenticate(
                request=request,
                username=identificador,
                password=password,
            )

        if user is None:
            registrar_login_fallido(request, user=usuario)
            if usuario and usuario.esta_bloqueado():
                raise AuthenticationFailed(
                    MENSAJE_CUENTA_BLOQUEADA,
                    code="account_locked",
                )
            raise AuthenticationFailed(
                MENSAJE_CREDENCIALES_INCORRECTAS,
                code="authorization",
            )

        try:
            from configuracion.models import ConfiguracionGlobal
            en_mantenimiento = ConfiguracionGlobal.obtener().modo_mantenimiento
        except Exception:
            en_mantenimiento = False
        if en_mantenimiento and not user.tiene_rango_minimo(NIVEL_ADMINISTRADOR):
            raise AuthenticationFailed(MENSAJE_MANTENIMIENTO, code="maintenance")

        attrs["username"] = user.get_username()
        data = super().validate(attrs)
        registrar_login_exitoso(request, user)
        return data
