import mimetypes

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from usuarios.constants import NIVEL_GESTION_USUARIOS
from usuarios.decorators import requiere_jerarquia

from .forms import DocumentoTrabajadorForm, TrabajadorForm
from .models import DocumentoTrabajador, Trabajador
from .utils import cambiar_estado_trabajador


def _contexto_base(extra=None):
    ctx = {"seccion_activa": "trabajadores"}
    if extra:
        ctx.update(extra)
    return ctx


def _puede_gestionar(user):
    return user.is_authenticated and user.tiene_rango_minimo(NIVEL_GESTION_USUARIOS)


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_GESTION_USUARIOS)
def lista_trabajadores(request):
    trabajadores = Trabajador.objects.select_related("cargo", "especialidad")
    q = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "").strip()

    if q:
        trabajadores = trabajadores.filter(
            Q(nombre__icontains=q)
            | Q(apellido__icontains=q)
            | Q(cedula__icontains=q)
        )
    if estado in Trabajador.Estado.values:
        trabajadores = trabajadores.filter(estado=estado)

    return render(
        request,
        "trabajadores/lista.html",
        _contexto_base(
            {
                "trabajadores": trabajadores,
                "busqueda": q,
                "filtro_estado": estado,
                "titulo": "Gestión de Trabajadores",
            }
        ),
    )


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_GESTION_USUARIOS)
def crear_trabajador(request):
    form = TrabajadorForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        trabajador = form.save()
        messages.success(request, "Trabajador registrado correctamente.")
        return redirect("trabajadores:detalle", trabajador_id=trabajador.pk)

    return render(
        request,
        "trabajadores/formulario.html",
        _contexto_base({"form": form, "titulo": "Nuevo Trabajador"}),
    )


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_GESTION_USUARIOS)
def editar_trabajador(request, trabajador_id):
    trabajador = get_object_or_404(Trabajador, pk=trabajador_id)
    form = TrabajadorForm(
        request.POST or None, request.FILES or None, instance=trabajador
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Trabajador actualizado correctamente.")
        return redirect("trabajadores:detalle", trabajador_id=trabajador.pk)

    return render(
        request,
        "trabajadores/formulario.html",
        _contexto_base(
            {
                "form": form,
                "trabajador": trabajador,
                "titulo": "Editar Trabajador",
            }
        ),
    )


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_GESTION_USUARIOS)
def detalle_trabajador(request, trabajador_id):
    """Perfil del trabajador y gestión de documentos (3.3)."""
    trabajador = get_object_or_404(
        Trabajador.objects.select_related("cargo", "especialidad"),
        pk=trabajador_id,
    )
    doc_form = DocumentoTrabajadorForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and doc_form.is_valid():
        documento = doc_form.save(commit=False)
        documento.trabajador = trabajador
        documento.subido_por = request.user
        documento.save()
        messages.success(request, "Documento subido correctamente.")
        return redirect("trabajadores:detalle", trabajador_id=trabajador.pk)

    return render(
        request,
        "trabajadores/detalle.html",
        _contexto_base(
            {
                "trabajador": trabajador,
                "documentos": trabajador.documentos.all(),
                "doc_form": doc_form,
                "titulo": f"Perfil — {trabajador}",
            }
        ),
    )


@login_required
@requiere_jerarquia(nivel_minimo=NIVEL_GESTION_USUARIOS)
def cambiar_estado(request, trabajador_id):
    if request.method != "POST":
        return redirect("trabajadores:lista")

    trabajador = get_object_or_404(Trabajador, pk=trabajador_id)
    nuevo = request.POST.get("estado") or None
    if nuevo and nuevo not in Trabajador.Estado.values:
        messages.error(request, "Estado no válido.")
        return redirect("trabajadores:lista")

    cambiar_estado_trabajador(trabajador, nuevo_estado=nuevo)
    label = trabajador.get_estado_display()
    messages.success(request, f"Estado actualizado a {label}.")

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "success": True,
                "estado": trabajador.estado,
                "mensaje": f"Estado actualizado a {label}.",
            }
        )
    return redirect(request.META.get("HTTP_REFERER", "trabajadores:lista"))


@login_required
def servir_foto(request, trabajador_id):
    """Sirve la foto solo a usuarios autorizados (3.4)."""
    if not _puede_gestionar(request.user):
        return HttpResponseForbidden()

    trabajador = get_object_or_404(Trabajador, pk=trabajador_id)
    if not trabajador.foto:
        raise Http404()

    return FileResponse(
        trabajador.foto.open("rb"),
        content_type=mimetypes.guess_type(trabajador.foto.name)[0]
        or "application/octet-stream",
    )


@login_required
def ver_documento(request, documento_id):
    """Visualización de documentos (3.3)."""
    if not _puede_gestionar(request.user):
        return HttpResponseForbidden()

    documento = get_object_or_404(DocumentoTrabajador, pk=documento_id)
    content_type = (
        mimetypes.guess_type(documento.archivo.name)[0] or "application/octet-stream"
    )
    response = FileResponse(documento.archivo.open("rb"), content_type=content_type)
    if content_type == "application/pdf":
        response["Content-Disposition"] = (
            f'inline; filename="{documento.titulo}.pdf"'
        )
    return response


@login_required
def descargar_documento(request, documento_id):
    if not _puede_gestionar(request.user):
        return HttpResponseForbidden()

    documento = get_object_or_404(DocumentoTrabajador, pk=documento_id)
    response = FileResponse(
        documento.archivo.open("rb"),
        as_attachment=True,
        filename=documento.archivo.name.split("/")[-1],
    )
    return response
