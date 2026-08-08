from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import timedelta

from .models import Guardia, Cronograma, AsignacionGuardia, AprobacionCronograma
from .forms import AsignacionGuardiaForm

def get_week_range(date):
    start = date - timedelta(days=date.weekday())
    end = start + timedelta(days=6)
    return start, end

@login_required
def asignar_turno(request):
    if request.method == 'POST':
        form = AsignacionGuardiaForm(request.POST)
        if form.is_valid():
            asignacion = form.save(commit=False)
            
            # Buscar o crear cronograma para esta semana
            start_date, end_date = get_week_range(asignacion.fecha)
            cronograma, created = Cronograma.objects.get_or_create(
                fecha_inicio=start_date,
                fecha_fin=end_date
            )
            
            asignacion.cronograma = cronograma
            asignacion.save()
            
            messages.success(request, 'Turno asignado exitosamente.')
            return redirect('guardias:asignar_turno')
        else:
            messages.error(request, 'Error al asignar el turno. Por favor verifica los datos.')
    else:
        form = AsignacionGuardiaForm()
        
    return render(request, 'guardias/asignar_turno.html', {'form': form})

@login_required
def cronograma_semanal(request):
    import datetime
    hoy = datetime.date.today()
    
    # Podemos permitir navegar entre semanas con un query param ?fecha=2026-05-20
    fecha_str = request.GET.get('fecha')
    if fecha_str:
        try:
            fecha_referencia = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            fecha_referencia = hoy
    else:
        fecha_referencia = hoy
        
    start_date, end_date = get_week_range(fecha_referencia)
    
    cronograma, created = Cronograma.objects.get_or_create(
        fecha_inicio=start_date,
        fecha_fin=end_date
    )
    
    asignaciones = AsignacionGuardia.objects.filter(cronograma=cronograma).select_related('trabajador', 'guardia')
    
    # Obtener el estado de aprobación (o crearlo)
    aprobacion, _ = AprobacionCronograma.objects.get_or_create(cronograma=cronograma)
    
    # Días de la semana para la cabecera
    dias = [start_date + timedelta(days=i) for i in range(7)]
    
    context = {
        'cronograma': cronograma,
        'asignaciones': asignaciones,
        'aprobacion': aprobacion,
        'dias': dias,
        'start_date': start_date,
        'end_date': end_date,
        'semana_anterior': (start_date - timedelta(days=7)).strftime('%Y-%m-%d'),
        'semana_siguiente': (start_date + timedelta(days=7)).strftime('%Y-%m-%d'),
        'seccion_activa': 'guardias', # Para activar el nav en base.html
    }
    return render(request, 'guardias/cronograma.html', context)

@login_required
def aprobar_cronograma(request, cronograma_id):
    if request.method == 'POST':
        # Validar que el usuario sea Gerente de guardias
        # (Esto asume que hay un atributo rol.nombre en el modelo User, como se ve en base.html)
        es_gerente = request.user.is_superuser or (hasattr(request.user, 'rol') and getattr(request.user.rol, 'nombre', '') == 'Gerente de guardias')
        
        if es_gerente:
            cronograma = get_object_or_404(Cronograma, id=cronograma_id)
            aprobacion, _ = AprobacionCronograma.objects.get_or_create(cronograma=cronograma)
            aprobacion.aprobado = True
            aprobacion.save()
            messages.success(request, 'El cronograma ha sido aprobado exitosamente.')
        else:
            messages.error(request, 'No tienes permisos para aprobar cronogramas. Se requiere rol de Gerente de guardias.')
            
    # Redirigir de vuelta al cronograma
    referencia = request.POST.get('fecha_referencia', '')
    url = '/guardias/cronograma/'
    if referencia:
        url += f'?fecha={referencia}'
    return redirect(url)
