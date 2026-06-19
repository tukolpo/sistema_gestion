from django.shortcuts import get_object_or_404
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from usuarios.constants import NIVEL_GESTION_USUARIOS
from usuarios.permissions import TieneJerarquiaMinima

from trabajadores.models import Trabajador
from trabajadores_ext.auditoria import registrar
from trabajadores_ext.models import AuditoriaTrabajador, EscaneoQR, TrabajadorTokenQR
from trabajadores_ext.qr import generar_imagen_qr, obtener_token_qr, url_perfil_publico


class PermisoGestion(TieneJerarquiaMinima):
    nivel_requerido = NIVEL_GESTION_USUARIOS


class AuditoriaTrabajadorSerializer(serializers.ModelSerializer):
    trabajador_nombre = serializers.SerializerMethodField()
    usuario_nombre = serializers.CharField(source="usuario.username", read_only=True)

    class Meta:
        model = AuditoriaTrabajador
        fields = (
            "id",
            "trabajador",
            "trabajador_nombre",
            "usuario",
            "usuario_nombre",
            "accion",
            "tabla",
            "registro_id",
            "valor_anterior",
            "valor_nuevo",
            "ip",
            "ruta",
            "creado_en",
        )

    def get_trabajador_nombre(self, obj):
        if obj.trabajador_id:
            return str(obj.trabajador)
        return None


class EscaneoQRSerializer(serializers.ModelSerializer):
    class Meta:
        model = EscaneoQR
        fields = ("id", "token_qr", "ip", "user_agent", "escaneado_en")


class TrabajadorQRSerializer(serializers.Serializer):
    token = serializers.UUIDField(read_only=True)
    url_publica = serializers.URLField(read_only=True)
    activo = serializers.BooleanField(read_only=True)
    escaneos = serializers.IntegerField(read_only=True)


class AuditoriaTrabajadorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditoriaTrabajador.objects.select_related("trabajador", "usuario")
    serializer_class = AuditoriaTrabajadorSerializer
    permission_classes = [IsAuthenticated, PermisoGestion]

    def get_queryset(self):
        qs = super().get_queryset()
        trabajador_id = self.request.query_params.get("trabajador")
        accion = self.request.query_params.get("accion")
        if trabajador_id:
            qs = qs.filter(trabajador_id=trabajador_id)
        if accion:
            qs = qs.filter(accion=accion)
        return qs


class TrabajadorQRViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, PermisoGestion]

    def retrieve(self, request, pk=None):
        trabajador = get_object_or_404(Trabajador, pk=pk)
        token_obj = obtener_token_qr(trabajador)
        registrar(
            AuditoriaTrabajador.Accion.QR_GENERADO,
            request=request,
            trabajador=trabajador,
            tabla="trabajadores_ext_trabajadortokenqr",
            registro_id=token_obj.pk,
            valor_nuevo=str(token_obj.token),
        )
        return Response(
            {
                "token": token_obj.token,
                "url_publica": url_perfil_publico(request, token_obj.token),
                "activo": token_obj.activo,
                "escaneos": token_obj.escaneos.count(),
            }
        )

    @action(detail=True, methods=["get"], url_path="imagen")
    def imagen(self, request, pk=None):
        trabajador = get_object_or_404(Trabajador, pk=pk)
        token_obj = obtener_token_qr(trabajador)
        url_publica = url_perfil_publico(request, token_obj.token)
        buffer = generar_imagen_qr(url_publica)
        from django.http import HttpResponse

        return HttpResponse(buffer.getvalue(), content_type="image/png")

    @action(detail=True, methods=["get"], url_path="escaneos")
    def escaneos(self, request, pk=None):
        trabajador = get_object_or_404(Trabajador, pk=pk)
        token_obj = obtener_token_qr(trabajador)
        data = EscaneoQRSerializer(token_obj.escaneos.all()[:100], many=True).data
        return Response(data)
