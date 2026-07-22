from rest_framework import serializers


class DisponibilidadFuncionarioSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    apellido = serializers.CharField()
    nombre_completo = serializers.CharField()
    cedula = serializers.CharField()
    cargo = serializers.CharField(allow_null=True)
    disponible = serializers.BooleanField()
    estado_disponibilidad = serializers.CharField()
    estado_disponibilidad_display = serializers.CharField()
    motivo = serializers.CharField(allow_null=True)
