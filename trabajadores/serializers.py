# trabajadores/serializers.py
# Serializers API CRUD (1.2)

from rest_framework import serializers

from trabajadores.models import Cargo, DocumentoTrabajador, Especialidad, Trabajador
from trabajadores.validators import validar_archivo_documento, validar_archivo_foto


class CargoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cargo
        fields = ("id", "nombre", "descripcion")


class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = ("id", "nombre", "descripcion")


class DocumentoTrabajadorSerializer(serializers.ModelSerializer):
    extension = serializers.CharField(read_only=True)
    subido_por_nombre = serializers.CharField(
        source="subido_por.username", read_only=True
    )

    class Meta:
        model = DocumentoTrabajador
        fields = (
            "id",
            "trabajador",
            "tipo",
            "titulo",
            "archivo",
            "extension",
            "subido_en",
            "subido_por",
            "subido_por_nombre",
        )
        read_only_fields = ("subido_en", "subido_por")

    def validate_archivo(self, archivo):
        validar_archivo_documento(archivo)
        return archivo

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["subido_por"] = request.user
        return super().create(validated_data)


class TrabajadorSerializer(serializers.ModelSerializer):
    cargo_nombre = serializers.CharField(source="cargo.nombre", read_only=True)
    especialidad_nombre = serializers.CharField(
        source="especialidad.nombre", read_only=True, allow_null=True
    )
    esta_activo = serializers.BooleanField(read_only=True)
    documentos = DocumentoTrabajadorSerializer(many=True, read_only=True)

    class Meta:
        model = Trabajador
        fields = (
            "id",
            "nombre",
            "apellido",
            "cedula",
            "fecha_nacimiento",
            "fecha_ingreso",
            "departamento",
            "cargo",
            "cargo_nombre",
            "especialidad",
            "especialidad_nombre",
            "estado",
            "esta_activo",
            "telefono",
            "email",
            "notas_perfil",
            "foto",
            "fecha_creacion",
            "fecha_actualizacion",
            "documentos",
        )
        read_only_fields = ("fecha_creacion", "fecha_actualizacion")

    def validate_foto(self, foto):
        validar_archivo_foto(foto)
        return foto

    def validate_estado(self, valor):
        if valor not in Trabajador.Estado.values:
            raise serializers.ValidationError("Estado no válido.")
        return valor


class TrabajadorEstadoSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(
        choices=Trabajador.Estado.choices,
        required=False,
        allow_null=True,
        help_text="Omitir para alternar entre activo e inactivo.",
    )
