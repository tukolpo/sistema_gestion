import threading
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.db import connection
from .models import LogAuditoria

# Thread-local para rastrear la request actual (usuario e IP)
_thread_locals = threading.local()

def set_current_request(request):
    _thread_locals.request = request

def get_current_user():
    request = getattr(_thread_locals, 'request', None)
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        return request.user
    return None

def get_client_ip():
    request = getattr(_thread_locals, 'request', None)
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    return None

def _tabla_auditoria_existe():
    """Verifica que la tabla de auditoría ya existe antes de escribir en ella."""
    try:
        return 'usuarios_logauditoria' in connection.introspection.table_names()
    except Exception:
        return False

def serializar_instancia(instance):
    try:
        data = model_to_dict(instance)
        for key, value in data.items():
            if hasattr(value, 'url'):
                data[key] = value.url
            elif value is not None:
                data[key] = str(value)
        return data
    except Exception:
        return {}

_MODELOS_IGNORADOS = frozenset([
    'LogAuditoria', 'Session', 'SecurityLog', 'LogEntry',
    'OutstandingToken', 'BlacklistedToken', 'Migration',
    'ContentType', 'Permission',
])

@receiver(pre_save)
def track_pre_save(sender, instance, **kwargs):
    if kwargs.get('raw', False):
        return
    if sender == LogAuditoria or sender.__name__ in _MODELOS_IGNORADOS:
        return
    try:
        if instance.pk:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_data = serializar_instancia(old_instance)
        else:
            instance._old_data = None
    except sender.DoesNotExist:
        instance._old_data = None

@receiver(post_save)
def track_post_save(sender, instance, created, **kwargs):
    if kwargs.get('raw', False):
        return
    if sender == LogAuditoria or sender.__name__ in _MODELOS_IGNORADOS:
        return
    if not _tabla_auditoria_existe():
        return

    user = get_current_user()
    ip = get_client_ip()
    new_data = serializar_instancia(instance)

    try:
        if created:
            LogAuditoria.objects.create(
                usuario=user,
                accion=LogAuditoria.Accion.CREAR,
                modelo_afectado=sender.__name__,
                registro_id=str(instance.pk),
                valores_anteriores=None,
                valores_nuevos=new_data,
                ip_address=ip
            )
        else:
            old_data = getattr(instance, '_old_data', {})
            if old_data != new_data:
                LogAuditoria.objects.create(
                    usuario=user,
                    accion=LogAuditoria.Accion.EDITAR,
                    modelo_afectado=sender.__name__,
                    registro_id=str(instance.pk),
                    valores_anteriores=old_data,
                    valores_nuevos=new_data,
                    ip_address=ip
                )
    except Exception:
        pass  # No interrumpir la operación principal si falla la auditoría

@receiver(post_delete)
def track_post_delete(sender, instance, **kwargs):
    if kwargs.get('raw', False):
        return
    if sender == LogAuditoria or sender.__name__ in _MODELOS_IGNORADOS:
        return
    if not _tabla_auditoria_existe():
        return

    user = get_current_user()
    ip = get_client_ip()
    old_data = serializar_instancia(instance)

    try:
        LogAuditoria.objects.create(
            usuario=user,
            accion=LogAuditoria.Accion.ELIMINAR,
            modelo_afectado=sender.__name__,
            registro_id=str(instance.pk),
            valores_anteriores=old_data,
            valores_nuevos=None,
            ip_address=ip
        )
    except Exception:
        pass
