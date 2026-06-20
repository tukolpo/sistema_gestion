from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from trabajadores.models import DocumentoTrabajador, Trabajador
from trabajadores_ext.auditoria import registrar
from trabajadores_ext.models import AuditoriaTrabajador


@receiver(pre_save, sender=Trabajador)
def _guardar_estado_previo(sender, instance, **kwargs):
    if instance.pk:
        try:
            previo = Trabajador.objects.get(pk=instance.pk)
            instance._estado_previo_auditoria = previo.estado
        except Trabajador.DoesNotExist:
            instance._estado_previo_auditoria = None
    else:
        instance._estado_previo_auditoria = None


@receiver(post_save, sender=Trabajador)
def _auditar_trabajador(sender, instance, created, **kwargs):
    if created:
        registrar(
            AuditoriaTrabajador.Accion.CREAR,
            trabajador=instance,
            tabla="trabajadores_trabajador",
            registro_id=instance.pk,
            valor_nuevo=f"{instance.nombre} {instance.apellido} · {instance.cedula}",
        )
        return
    previo = getattr(instance, "_estado_previo_auditoria", None)
    if previo is not None and previo != instance.estado:
        registrar(
            AuditoriaTrabajador.Accion.ESTADO,
            trabajador=instance,
            tabla="trabajadores_trabajador",
            registro_id=instance.pk,
            valor_anterior=previo,
            valor_nuevo=instance.estado,
        )
    registrar(
        AuditoriaTrabajador.Accion.ACTUALIZAR,
        trabajador=instance,
        tabla="trabajadores_trabajador",
        registro_id=instance.pk,
    )


@receiver(post_delete, sender=Trabajador)
def _auditar_borrado_trabajador(sender, instance, **kwargs):
    registrar(
        AuditoriaTrabajador.Accion.ELIMINAR,
        tabla="trabajadores_trabajador",
        registro_id=instance.pk,
        valor_anterior=f"{instance.nombre} {instance.apellido}",
    )


@receiver(post_save, sender=DocumentoTrabajador)
def _auditar_documento(sender, instance, created, **kwargs):
    registrar(
        AuditoriaTrabajador.Accion.DOCUMENTO,
        trabajador=instance.trabajador,
        tabla="trabajadores_documentotrabajador",
        registro_id=instance.pk,
        valor_nuevo=f"{instance.titulo} ({instance.get_tipo_display()})",
    )


@receiver(post_delete, sender=DocumentoTrabajador)
def _auditar_borrado_documento(sender, instance, **kwargs):
    registrar(
        AuditoriaTrabajador.Accion.ELIMINAR,
        trabajador=instance.trabajador,
        tabla="trabajadores_documentotrabajador",
        registro_id=instance.pk,
        valor_anterior=instance.titulo,
    )
