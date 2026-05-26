from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from usuarios.backends import EmailBackend


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Acepta correo en el campo ``username`` del JSON (igual que el login web).
    """

    def validate(self, attrs):
        identificador = (attrs.get("username") or "").strip()
        password = attrs.get("password")

        user = EmailBackend().authenticate(
            request=self.context.get("request"),
            username=identificador,
            password=password,
        )
        if user is None:
            user = authenticate(
                request=self.context.get("request"),
                username=identificador,
                password=password,
            )
        if user is not None:
            attrs["username"] = user.get_username()

        return super().validate(attrs)
