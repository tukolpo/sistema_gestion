from django.contrib import messages
from django.shortcuts import redirect, render
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
    }
    return render(request, 'configuracion/ajustes_globales.html', context)