# usuarios/signals.py
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from usuarios.security import establecer_sesion_unica, liberar_sesion_activa


@receiver(user_logged_in)
def al_iniciar_sesion(sender, request, user, **kwargs):
    """Se dispara en CUALQUIER login (web, /admin/, etc.), no solo en vista_login."""
    if request is None or not hasattr(user, "sesion_clave_activa"):
        return
    establecer_sesion_unica(request, user)


@receiver(user_logged_out)
def al_cerrar_sesion(sender, request, user, **kwargs):
    """Libera la clave activa solo si la sesión que se cierra es la activa."""
    if request is None or user is None:
        return
    liberar_sesion_activa(request, user)