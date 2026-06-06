# usuarios/api_views.py
# Vistas API REST (JWT, perfil)

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.constants import NIVEL_OPERATIVO
from usuarios.permissions import TieneJerarquiaMinima


class PerfilAPIView(APIView):
    permission_classes = [IsAuthenticated, TieneJerarquiaMinima]
    nivel_requerido = NIVEL_OPERATIVO

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.pk,
                "username": user.username,
                "email": user.email,
                "rol": user.rol.nombre if user.rol else None,
                "nivel": user.rol.nivel_jerarquia if user.rol else 0,
            }
        )
