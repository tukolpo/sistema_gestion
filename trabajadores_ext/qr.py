import io

import qrcode
from django.urls import reverse

from trabajadores_ext.models import TrabajadorTokenQR


def obtener_token_qr(trabajador):
    token_obj, _ = TrabajadorTokenQR.objects.get_or_create(trabajador=trabajador)
    return token_obj


def url_perfil_publico(request, token):
    path = reverse("trabajadores_ext:perfil_publico", kwargs={"token": token})
    return request.build_absolute_uri(path)


def generar_imagen_qr(contenido):
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(contenido)
    qr.make(fit=True)
    imagen = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
