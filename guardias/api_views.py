from datetime import datetime

from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from usuarios.constants import NIVEL_GESTION_USUARIOS
from usuarios.permissions import TieneJerarquiaMinima

from guardias.serializers import DisponibilidadFuncionarioSerializer
from guardias.services import consultar_disponibilidad


class PermisoGestionGuardias(TieneJerarquiaMinima):
    nivel_requerido = NIVEL_GESTION_USUARIOS


class DisponibilidadAPIView(APIView):
    """Consulta la disponibilidad de funcionarios desde la base de datos."""

    permission_classes = [IsAuthenticated, PermisoGestionGuardias]
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    def get(self, request):
        fecha_param = request.query_params.get("fecha")
        fecha = None
        if fecha_param:
            try:
                fecha = datetime.strptime(fecha_param, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"detail": "Formato de fecha inválido. Use YYYY-MM-DD."},
                    status=400,
                )

        datos = consultar_disponibilidad(fecha)
        serializer = DisponibilidadFuncionarioSerializer(datos, many=True)
        return Response(serializer.data)
