import csv
import io
import mimetypes
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import (
    FileResponse,
    Http404,
    HttpResponse,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from usuarios.constants import NIVEL_GESTION_USUARIOS
from usuarios.decorators import requiere_jerarquia

from .forms import DocumentoTrabajadorForm, TrabajadorForm
from .models import Cargo, DocumentoTrabajador, Trabajador
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
                "cargos": Cargo.objects.all(),
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
    documento = get_object_or_404(DocumentoTrabajador, pk=documento_id)
    response = FileResponse(
        documento.archivo.open("rb"),
        as_attachment=True,
        filename=documento.archivo.name.split("/")[-1],
    )
    return response


def perfil_publico_trabajador(request, trabajador_uuid):
    """Vista pública para verificar un trabajador mediante su código QR."""
    trabajador = get_object_or_404(Trabajador.objects.select_related("cargo", "especialidad"), uuid=trabajador_uuid)
    return render(
        request,
        "trabajadores/perfil_publico.html",
        {"trabajador": trabajador, "titulo": f"Perfil de {trabajador.nombre}"}
    )


# ───────────────────────────────────────────────────────────
# Tarea 4: Generación de Planillas Personalizadas (exportación)
# ───────────────────────────────────────────────────────────

COLUMNAS_EXPORT = {
    "cedula": "Cédula", "nombre": "Nombre completo", "cargo": "Cargo",
    "departamento": "Departamento", "estatus": "Estatus",
    "fecha_ingreso": "Fecha de ingreso", "antiguedad": "Antigüedad",
}
ROLES_EXPORTACION = {"admin", "rrhh", "supervisor"}


def _puede_exportar(user):
    return user.is_superuser or user.groups.filter(name__in=ROLES_EXPORTACION).exists()


def _antiguedad_texto(fecha_ingreso):
    if not fecha_ingreso:
        return "—"
    delta = datetime.today().date() - fecha_ingreso
    años, meses = delta.days // 365, (delta.days % 365) // 30
    if años == 0: return f"{meses} mes(es)"
    if meses == 0: return f"{años} año(s)"
    return f"{años} año(s) y {meses} mes(es)"


def _qs_a_registros(qs):
    return [{
        "cedula": t.cedula,
        "nombre": f"{t.nombre} {t.apellido}",
        "cargo": t.cargo.nombre if t.cargo else "—",
        "departamento": t.departamento or "—",
        "estatus": t.get_estado_display(),
        "fecha_ingreso": t.fecha_ingreso.strftime("%d/%m/%Y") if t.fecha_ingreso else "—",
        "antiguedad": _antiguedad_texto(t.fecha_ingreso),
    } for t in qs]


def _leer_filtros(request):
    return {c: request.GET[c] for c in ["cargo", "departamento", "estatus", "antiguedad"] if request.GET.get(c)}


def _aplicar_filtros(filtros):
    from django.utils import timezone
    from datetime import timedelta
    qs = Trabajador.objects.select_related("cargo")
    if filtros.get("cargo"):         qs = qs.filter(cargo_id=filtros["cargo"])
    if filtros.get("departamento"):  qs = qs.filter(departamento__icontains=filtros["departamento"])
    if filtros.get("estatus"):       qs = qs.filter(estado=filtros["estatus"])
    if filtros.get("antiguedad"):
        hoy = timezone.now().date()
        try:
            años = int(filtros["antiguedad"])
        except ValueError:
            años = None
        if años is not None:
            qs = qs.filter(fecha_ingreso__lte=hoy - timedelta(days=365 * años))
    return qs.order_by("apellido", "nombre")


def _nombre_archivo(filtros, ext):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    partes = ["planilla"] + [filtros[k].replace(" ", "_").lower() for k in ["departamento", "estatus"] if filtros.get(k)] + [ts]
    return f"{'_'.join(partes)}.{ext}"


def _titulo_export(filtros):
    partes = ["Planilla de Trabajadores"]
    if filtros.get("departamento"): partes.append(f"– Depto.: {filtros['departamento']}")
    if filtros.get("cargo"):
        cargo_obj = Cargo.objects.filter(pk=filtros["cargo"]).first()
        if cargo_obj:
            partes.append(f"– Cargo: {cargo_obj.nombre}")
    if filtros.get("estatus"):      partes.append(f"– Estatus: {filtros['estatus']}")
    return " ".join(partes)


@login_required
@require_GET
def exportar_excel(request):
    if not _puede_exportar(request.user):
        messages.error(request, "No tienes permiso para exportar datos.")
        return redirect("trabajadores:lista")
    filtros = _leer_filtros(request)
    qs = _aplicar_filtros(filtros)
    if not qs.exists():
        messages.warning(request, "No se encontraron resultados para exportar con los filtros aplicados.")
        return redirect("trabajadores:lista")
    registros = _qs_a_registros(qs)
    df = pd.DataFrame(registros).rename(columns=COLUMNAS_EXPORT)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Trabajadores", index=False, startrow=3)
        wb, ws = writer.book, writer.sheets["Trabajadores"]
        fmt_enc  = wb.add_format({"bold":True,"bg_color":"#1A3A5C","font_color":"#FFFFFF","border":1,"align":"center"})
        fmt_alt  = wb.add_format({"border":1,"bg_color":"#F0F4F8"})
        fmt_norm = wb.add_format({"border":1})
        fmt_tot  = wb.add_format({"bold":True,"bg_color":"#2E86C1","font_color":"#FFFFFF","border":1})
        ws.write(0, 0, _titulo_export(filtros), wb.add_format({"bold":True,"font_size":14,"font_color":"#1A3A5C"}))
        ws.write(1, 0, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", wb.add_format({"italic":True,"font_size":9}))
        ws.write(2, 0, f"Total: {len(registros)} registros", wb.add_format({"italic":True,"font_size":9}))
        for i, col in enumerate(df.columns): ws.write(3, i, col, fmt_enc)
        for r in range(len(registros)):
            for c in range(len(df.columns)):
                ws.write(r+4, c, df.iloc[r,c], fmt_alt if r%2==0 else fmt_norm)
        fila_tot = len(registros)+4
        ws.write(fila_tot, 0, f"Total: {len(registros)}", fmt_tot)
        for c in range(1, len(df.columns)): ws.write(fila_tot, c, "", fmt_tot)
        for i, col in enumerate(df.columns): ws.set_column(i, i, min(max(len(col),10)+4, 40))
        ws.set_row(3, 30)
        ws.freeze_panes(4, 0)
    buf.seek(0)
    resp = HttpResponse(buf, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    resp["Content-Disposition"] = f'attachment; filename="{_nombre_archivo(filtros,"xlsx")}"'
    return resp


@login_required
@require_GET
def exportar_csv(request):
    if not _puede_exportar(request.user):
        messages.error(request, "No tienes permiso para exportar datos.")
        return redirect("trabajadores:lista")
    filtros = _leer_filtros(request)
    qs = _aplicar_filtros(filtros)
    if not qs.exists():
        messages.warning(request, "No se encontraron resultados para exportar con los filtros aplicados.")
        return redirect("trabajadores:lista")
    registros = _qs_a_registros(qs)
    buf = io.StringIO()
    buf.write(f"# {_titulo_export(filtros)}\n# Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n# Total: {len(registros)}\n#\n")
    w = csv.DictWriter(buf, fieldnames=list(COLUMNAS_EXPORT.keys()), extrasaction="ignore")
    w.writerow(COLUMNAS_EXPORT)
    w.writerows(registros)
    resp = HttpResponse("\ufeff" + buf.getvalue(), content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename="{_nombre_archivo(filtros,"csv")}"'
    return resp


@login_required
@require_GET
def exportar_pdf(request):
    if not _puede_exportar(request.user):
        messages.error(request, "No tienes permiso para exportar datos.")
        return redirect("trabajadores:lista")
    filtros = _leer_filtros(request)
    qs = _aplicar_filtros(filtros)
    if not qs.exists():
        messages.warning(request, "No se encontraron resultados para exportar con los filtros aplicados.")
        return redirect("trabajadores:lista")
    registros = _qs_a_registros(qs)
    buf = io.BytesIO()
    primario = colors.HexColor("#1A3A5C")
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=2*cm, bottomMargin=2*cm)
    estilos = getSampleStyleSheet()
    historia = [
        Paragraph(_titulo_export(filtros), ParagraphStyle("T", parent=estilos["Heading1"], textColor=primario, fontSize=16, spaceAfter=4)),
        Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}  |  Total: <b>{len(registros)}</b>",
                  ParagraphStyle("S", parent=estilos["Normal"], textColor=colors.HexColor("#555555"), fontSize=9)),
        HRFlowable(width="100%", thickness=2, color=primario, spaceAfter=10),
    ]
    filas = [list(COLUMNAS_EXPORT.values())] + [[r[k] for k in COLUMNAS_EXPORT] for r in registros]
    tabla = Table(filas, repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),primario), ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"), ("FONTSIZE",(0,0),(-1,0),9),
        ("ALIGN",(0,0),(-1,0),"CENTER"), ("BOTTOMPADDING",(0,0),(-1,0),8),
        ("FONTNAME",(0,1),(-1,-1),"Helvetica"), ("FONTSIZE",(0,1),(-1,-1),8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#F0F4F8")]),
        ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#CCCCCC")),
    ]))
    historia += [tabla, Spacer(1,0.5*cm),
                 Paragraph("Documento generado por el Sistema de Gestión de Personal — Uso interno",
                            ParagraphStyle("P", parent=estilos["Normal"], textColor=colors.HexColor("#888888"), fontSize=8, alignment=TA_CENTER))]
    doc.build(historia)
    buf.seek(0)
    resp = HttpResponse(buf, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="{_nombre_archivo(filtros,"pdf")}"'
    return resp