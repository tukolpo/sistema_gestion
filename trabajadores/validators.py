"""Validadores de formato y peso para archivos (3.2)."""

import os

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
