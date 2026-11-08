# configuracion/context_processors.py
from configuracion.models import ConfiguracionGlobal
from usuarios.constants import MENSAJE_MANTENIMIENTO

# Temas de color: clave -> (nombre, principal, oscuro, claro, fondo, fondo claro)
# Se corresponden con --color-burdeos, -dark, -light, --color-rosa y -rosa-light de styles.css
TEMAS = {
    "azul":    ("Azul",    "#7EAEDF", "#5B8AB8", "#A3C9EE", "#DCEAFC", "#EDF4FD"),
    "verde":   ("Verde",   "#6DBF8F", "#3F8F63", "#9AD6B2", "#D9F0E2", "#EDF8F2"),
    "violeta": ("Violeta", "#9B8AD9", "#6F5CB8", "#BDB1E8", "#E6E1F7", "#F3F0FB"),
    "rojo":    ("Rojo",    "#D9707A", "#B04552", "#E8A0A7", "#F8DDE0", "#FCEEF0"),
    "naranja": ("Naranja", "#E8A15A", "#C47A2C", "#F0C08C", "#FBE8D2", "#FDF4E9"),
    "gris":    ("Gris",    "#8A9BAE", "#5F6F82", "#B4C0CD", "#E3E8EE", "#F1F4F7"),
    # Tema estacional (los adornos están en temas.css)
    "navidad":   ("Navidad",   "#dc2626", "#14532d", "#16a34a", "#fee2e2", "#f0fdf4"),
}
TEMA_POR_DEFECTO = "azul"


def _css_tema(clave):
    _, base, oscuro, claro, fondo, fondo_claro = TEMAS.get(clave, TEMAS[TEMA_POR_DEFECTO])
    return (
        "<style id=\"tema-sistema\">:root{"
        f"--color-burdeos:{base};--color-burdeos-dark:{oscuro};--color-burdeos-light:{claro};"
        f"--color-rosa:{fondo};--color-rosa-light:{fondo_claro};"
        "}</style>"
    )


def mantenimiento(request):
    """Expone el estado del mantenimiento y el tema de color a todas las plantillas."""
    try:
        config = ConfiguracionGlobal.obtener()
        activo = bool(config.modo_mantenimiento)
        tema = getattr(config, "tema", TEMA_POR_DEFECTO)
    except Exception:
        activo = False
        tema = TEMA_POR_DEFECTO
    if tema not in TEMAS:
        tema = TEMA_POR_DEFECTO
    return {
        "en_mantenimiento": activo,
        "mensaje_mantenimiento": MENSAJE_MANTENIMIENTO,
        "tema_css": _css_tema(tema),
        "tema_activo": tema,
    }