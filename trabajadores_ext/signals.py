from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from trabajadores.models import DocumentoTrabajador, Trabajador
from trabajadores_ext.auditoria import registrar
from trabajadores_ext.current_user import obtener_usuario_actual
from trabajadores_ext.models import AuditoriaTrabajador

# Campos que nos interesa auditar cuando se edita un trabajador,
# con la etiqueta legible que se mostrará en el detalle.
_CAMPOS_AUDITADOS = [
    ("nombre", "Nombre"),
    ("apellido", "Apellido"),
    ("cedula", "Cédula"),
    ("telefono", "Teléfono"),
    ("email", "Email"),
    ("fecha_nacimiento", "Fecha de nacimiento"),
    ("fecha_ingreso", "Fecha de ingreso"),
    ("cargo", "Cargo"),
    ("especialidad", "Especialidad"),
    ("notas_perfil", "Notas del perfil"),
]


def _texto(valor):
    if valor in (None, ""):
        return "—"
    return str(valor)


def _resumen_cambios(previo, actual):
    """Compara campo por campo y arma una lista de textos tipo
    'Cargo: Administrativo → General' solo para lo que realmente cambió."""
    cambios = []
    for attr, etiqueta in _CAMPOS_AUDITADOS:
        valor_previo = getattr(previo, attr, None)
        valor_actual = getattr(actual, attr, None)
        if valor_previo != valor_actual:
            cambios.append(
                f"{etiqueta}: {_texto(valor_previo)} → {_texto(valor_actual)}"
            )
    return cambios


@receiver(pre_save, sender=Trabajador)
def _guardar_estado_previo(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._snapshot_previo = Trabajador.objects.select_related(
                "cargo", "especialidad"
            ).get(pk=instance.pk)
        except Trabajador.DoesNotExist:
            instance._snapshot_previo = None
    else:
        instance._snapshot_previo = None


@receiver(post_save, sender=Trabajador)
def _auditar_trabajador(sender, instance, created, **kwargs):
    usuario_actual = obtener_usuario_actual()

    if created:
        registrar(
            AuditoriaTrabajador.Accion.CREAR,
            usuario=usuario_actual,
            trabajador=instance,
            tabla="trabajadores_trabajador",
            registro_id=instance.pk,
            valor_nuevo=f"{instance.nombre} {instance.apellido} · {instance.cedula}",
        )
        return

    previo = getattr(instance, "_snapshot_previo", None)
    if previo is None:
        # No hay snapshot disponible (ej. actualización masiva por queryset.update()),
        # así que no podemos comparar campo por campo: no registramos nada vacío.
        return

    # Cambio de estado (activo/inactivo) se registra aparte, con su propia etiqueta
    if previo.estado != instance.estado:
        registrar(
            AuditoriaTrabajador.Accion.ESTADO,
            usuario=usuario_actual,
            trabajador=instance,
            tabla="trabajadores_trabajador",
            registro_id=instance.pk,
            valor_anterior=previo.get_estado_display(),
            valor_nuevo=instance.get_estado_display(),
        )

    # Resto de campos: solo se registra si de verdad hubo un cambio de datos
    cambios = _resumen_cambios(previo, instance)
    if cambios:
        registrar(
            AuditoriaTrabajador.Accion.ACTUALIZAR,
            usuario=usuario_actual,
            trabajador=instance,
            tabla="trabajadores_trabajador",
            registro_id=instance.pk,
            valor_nuevo="; ".join(cambios),
        )


@receiver(post_delete, sender=Trabajador)
def _auditar_borrado_trabajador(sender, instance, **kwargs):
    registrar(
        AuditoriaTrabajador.Accion.ELIMINAR,
        usuario=obtener_usuario_actual(),
        tabla="trabajadores_trabajador",
        registro_id=instance.pk,
        valor_anterior=f"{instance.nombre} {instance.apellido} · {instance.cedula}",
    )


@receiver(post_save, sender=DocumentoTrabajador)
def _auditar_documento(sender, instance, created, **kwargs):
    if not created:
        return
    registrar(
        AuditoriaTrabajador.Accion.DOCUMENTO,
        usuario=obtener_usuario_actual(),
        trabajador=instance.trabajador,
        tabla="trabajadores_documentotrabajador",
        registro_id=instance.pk,
        valor_nuevo=f"{instance.titulo} ({instance.get_tipo_display()})",
    )


@receiver(post_delete, sender=DocumentoTrabajador)
def _auditar_borrado_documento(sender, instance, **kwargs):
    registrar(
        AuditoriaTrabajador.Accion.ELIMINAR,
        usuario=obtener_usuario_actual(),
        trabajador=instance.trabajador,
        tabla="trabajadores_documentotrabajador",
        registro_id=instance.pk,
        valor_anterior=instance.titulo,
    )