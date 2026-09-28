"""
Permite que las señales (signals.py), que no reciben el `request`,
sepan qué usuario está autenticado durante la petición actual.
"""
import threading

_hilo_local = threading.local()


def establecer_usuario_actual(user):
    _hilo_local.user = user


def obtener_usuario_actual():
    return getattr(_hilo_local, "user", None)


def limpiar_usuario_actual():
    _hilo_local.user = None