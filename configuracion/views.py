from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from usuarios.constants import NIVEL_ADMINISTRADOR
from usuarios.decorators import requiere_jerarquia
from configuracion.forms import ConfiguracionGlobalForm
from configuracion.models import ConfiguracionGlobal


@requiere_jerarquia(nivel_minimo=NIVEL_ADMINISTRADOR)
def ajustes_globales(request):
    """
    Vista para visualizar y editar la configuración global del sistema
    bajo el patrón Singleton (pk=1). Restringida exclusivamente a administradores.
    """
    configuracion, created = ConfiguracionGlobal.objects.get_or_create(pk=1)

    if request.method == 'POST':
        form = ConfiguracionGlobalForm(request.POST, instance=configuracion)
        if form.is_valid():
            form.save()
            messages.success(request, "La configuración global se guardó correctamente.")
            return redirect('configuracion:ajustes_globales')
    else:
        form = ConfiguracionGlobalForm(instance=configuracion)

    context = {
        'titulo': 'Ajustes globales',
        'form': form,
        'seccion_activa': 'configuracion',
    }
    return render(request, 'configuracion/ajustes_globales.html', context)


@requiere_jerarquia(nivel_minimo=NIVEL_ADMINISTRADOR)
def control_sesiones(request):
    """Lista las sesiones activas del sistema (usuario y fecha de expiración)."""
    Usuario = get_user_model()
    sesiones_db = Session.objects.filter(expire_date__gte=timezone.now()).order_by('expire_date')
    sesion_actual = request.session.session_key

    usuarios_por_id = {
        str(usuario.pk): usuario
        for usuario in Usuario.objects.all()
    }

    sesiones = []
    for sesion in sesiones_db:
        datos = sesion.get_decoded()
        user_id = datos.get('_auth_user_id')
        sesiones.append({
            'session_key': sesion.session_key,
            'usuario': usuarios_por_id.get(str(user_id)) if user_id else None,
            'expire_date': sesion.expire_date,
            'es_sesion_actual': sesion.session_key == sesion_actual,
        })

    context = {
        'titulo': 'Control de sesiones',
        'sesiones': sesiones,
        'seccion_activa': 'configuracion',
    }
    return render(request, 'configuracion/control_sesiones.html', context)


@requiere_jerarquia(nivel_minimo=NIVEL_ADMINISTRADOR)
@require_POST
def cerrar_sesion_admin(request, session_key):
    """Permite al administrador forzar el cierre de una sesión específica."""
    if session_key == request.session.session_key:
        logout(request)
        return redirect('usuarios:login')

    sesion = get_object_or_404(Session, session_key=session_key)
    sesion.delete()
    messages.success(request, "La sesión se cerró correctamente.")
    return redirect('configuracion:control_sesiones')

