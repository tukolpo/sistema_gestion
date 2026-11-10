# trabajadores/serializers.py
# Serializers API CRUD (1.2)

from django.utils import timezone
from rest_framework import serializers

from trabajadores.antiguedad import MAYORIA_DE_EDAD, es_mayor_de_edad, texto_antiguedad
from trabajadores.models import DocumentoTrabajador, Especialidad, Trabajador
from trabajadores.validators import (
    normalizar_cedula,
    validar_archivo_documento,
    validar_archivo_foto,
    validar_cedula_venezuela,
)


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


def calcular_antiguedad(fecha_ingreso):
    if not fecha_ingreso:
        return None
    hoy = timezone.now().date()
    anios = hoy.year - fecha_ingreso.year
    if (hoy.month, hoy.day) < (fecha_ingreso.month, fecha_ingreso.day):
        anios -= 1
    return max(anios, 0)


class TrabajadorSerializer(serializers.ModelSerializer):
    especialidad_nombre = serializers.CharField(
        source="especialidad.nombre", read_only=True, allow_null=True
    )
    esta_activo = serializers.BooleanField(read_only=True)
    antiguedad = serializers.SerializerMethodField()
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
            "antiguedad",
            "departamento",
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
        extra_kwargs = {
            "fecha_nacimiento": {"required": True, "allow_null": False},
            "telefono": {"required": True, "allow_blank": False},
            "email": {"required": True, "allow_blank": False},
        }

    def get_antiguedad(self, obj):
        return calcular_antiguedad(obj.fecha_ingreso)

    def validate_cedula(self, valor):
        valor = normalizar_cedula(valor)
        validar_cedula_venezuela(valor)

        qs = Trabajador.objects.filter(cedula=valor)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un trabajador con esta cédula.")

        return valor

    def validate_fecha_nacimiento(self, fecha):
        if fecha and not es_mayor_de_edad(fecha):
            raise serializers.ValidationError(
                f"El trabajador debe ser mayor de {MAYORIA_DE_EDAD} años."
            )
        return fecha

    def validate_foto(self, foto):
        validar_archivo_foto(foto)
        return foto

    def validate_estado(self, valor):
        if valor not in Trabajador.Estado.values:
            raise serializers.ValidationError("Estado no válido.")
        return valor


class TrabajadorListSerializer(serializers.ModelSerializer):
    esta_activo = serializers.BooleanField(read_only=True)
    antiguedad = serializers.SerializerMethodField()
    antiguedad_texto = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)

    class Meta:
        model = Trabajador
        fields = (
            "id",
            "nombre",
            "apellido",
            "cedula",
            "departamento",
            "estado",
            "estado_display",
            "esta_activo",
            "fecha_ingreso",
            "antiguedad",
            "antiguedad_texto",
        )

    def get_antiguedad(self, obj):
        return calcular_antiguedad(obj.fecha_ingreso)

    def get_antiguedad_texto(self, obj):
        return texto_antiguedad(obj.fecha_ingreso)


class TrabajadorEstadoSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(
        choices=Trabajador.Estado.choices,
        required=False,
        allow_null=True,
        help_text="Omitir para alternar entre activo e inactivo.",
    )