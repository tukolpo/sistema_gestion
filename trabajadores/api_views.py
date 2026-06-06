# trabajadores/api_views.py
# Endpoints API CRUD (1.2)

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from usuarios.constants import NIVEL_GESTION_USUARIOS
from usuarios.permissions import TieneJerarquiaMinima

from trabajadores.models import Cargo, DocumentoTrabajador, Especialidad, Trabajador
from trabajadores.serializers import (
    CargoSerializer,
    DocumentoTrabajadorSerializer,
    EspecialidadSerializer,
    TrabajadorEstadoSerializer,
    TrabajadorSerializer,
)
from trabajadores.utils import cambiar_estado_trabajador


class PermisoGestionTrabajadores(TieneJerarquiaMinima):
    nivel_requerido = NIVEL_GESTION_USUARIOS


class CargoViewSet(viewsets.ModelViewSet):
    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer
    permission_classes = [IsAuthenticated, PermisoGestionTrabajadores]


class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer
    permission_classes = [IsAuthenticated, PermisoGestionTrabajadores]


class TrabajadorViewSet(viewsets.ModelViewSet):
    queryset = Trabajador.objects.select_related("cargo", "especialidad").prefetch_related(
        "documentos"
    )
    serializer_class = TrabajadorSerializer
    permission_classes = [IsAuthenticated, PermisoGestionTrabajadores]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        qs = super().get_queryset()
        estado = self.request.query_params.get("estado")
        if estado:
            qs = qs.filter(estado=estado)
        cargo_id = self.request.query_params.get("cargo")
        if cargo_id:
            qs = qs.filter(cargo_id=cargo_id)
        return qs

    @action(detail=True, methods=["post"], url_path="estado")
    def cambiar_estado(self, request, pk=None):
        trabajador = self.get_object()
        serializer = TrabajadorEstadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cambiar_estado_trabajador(
            trabajador, nuevo_estado=serializer.validated_data.get("estado")
        )
        return Response(TrabajadorSerializer(trabajador).data)

    @action(detail=True, methods=["get", "post"], url_path="documentos")
    def documentos(self, request, pk=None):
        trabajador = self.get_object()
        if request.method == "GET":
            docs = trabajador.documentos.all()
            return Response(DocumentoTrabajadorSerializer(docs, many=True).data)

        data = request.data.copy()
        data["trabajador"] = trabajador.pk
        serializer = DocumentoTrabajadorSerializer(
            data=data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(trabajador=trabajador)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DocumentoTrabajadorViewSet(viewsets.ModelViewSet):
    queryset = DocumentoTrabajador.objects.select_related("trabajador", "subido_por")
    serializer_class = DocumentoTrabajadorSerializer
    permission_classes = [IsAuthenticated, PermisoGestionTrabajadores]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = super().get_queryset()
        trabajador_id = self.request.query_params.get("trabajador")
        if trabajador_id:
            qs = qs.filter(trabajador_id=trabajador_id)
        return qs
