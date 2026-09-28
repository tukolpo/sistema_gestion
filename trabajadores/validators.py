"""Validadores de formato y peso para archivos (3.2), y de cédula venezolana."""

import os
import re

from django.core.exceptions import ValidationError

from trabajadores.constants import (
    EXTENSIONES_DOCUMENTO,
    EXTENSIONES_FOTO,
    MAX_DOCUMENTO_BYTES,
    MAX_FOTO_BYTES,
)


def _extension(filename):
    return os.path.splitext(filename)[1].lstrip(".").lower()


def validar_archivo_foto(archivo):
    if archivo is None:
        return
    ext = _extension(archivo.name)
    if ext not in EXTENSIONES_FOTO:
        raise ValidationError(
            f"Formato no permitido. Use: {', '.join(EXTENSIONES_FOTO)}."
        )
    if archivo.size > MAX_FOTO_BYTES:
        raise ValidationError(
            f"La foto no puede superar {MAX_FOTO_BYTES // (1024 * 1024)} MB."
        )


def validar_archivo_documento(archivo):
    if archivo is None:
        return
    ext = _extension(archivo.name)
    if ext not in EXTENSIONES_DOCUMENTO:
        raise ValidationError(
            f"Formato no permitido. Use: {', '.join(EXTENSIONES_DOCUMENTO)}."
        )
    if archivo.size > MAX_DOCUMENTO_BYTES:
        raise ValidationError(
            f"El documento no puede superar {MAX_DOCUMENTO_BYTES // (1024 * 1024)} MB."
        )


# ─── Cédula venezolana (V/E + 7 u 8 dígitos) ──────────────────────────
# Formato final almacenado: "V-12345678" o "E-1234567"  (máx. 10 caracteres)
CEDULA_REGEX = re.compile(r"^[VE]-\d{7,8}$")


def normalizar_cedula(valor):
    """Limpia y estandariza la cédula a formato 'V-12345678'.
    Acepta variantes de entrada como 'v12345678', 'V 12345678',
    'v-12345678' o solo '12345678' (asume V por defecto).
    """
    if not valor:
        return valor

    valor = valor.strip().upper().replace(" ", "").replace(".", "")

    if valor and valor[0] in ("V", "E"):
        prefijo = valor[0]
        resto = valor[1:].lstrip("-")
    else:
        prefijo = "V"
        resto = valor.lstrip("-")

    return f"{prefijo}-{resto}"


def validar_cedula_venezuela(valor):
    if not valor:
        raise ValidationError("La cédula es obligatoria.")
    if not CEDULA_REGEX.match(valor):
        raise ValidationError(
            "Cédula inválida. Usa el formato V-12345678 o E-1234567 (7 u 8 dígitos)."
        )