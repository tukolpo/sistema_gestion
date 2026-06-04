"""
Niveles jerárquicos RBAC del Módulo 1.
A mayor número, más privilegios.
"""

NIVEL_ADMINISTRADOR = 100
NIVEL_SUPERVISOR = 50
NIVEL_OPERATIVO = 10

# Umbrales usados en vistas
NIVEL_GESTION_USUARIOS = NIVEL_SUPERVISOR
NIVEL_ASIGNAR_ROLES = NIVEL_ADMINISTRADOR

# Bloqueo por intentos fallidos de login (Tarea 4)
MAX_INTENTOS_LOGIN = 5
MINUTOS_BLOQUEO_LOGIN = 5

MENSAJE_CREDENCIALES_INCORRECTAS = "Usuario o contraseña incorrectos"
MENSAJE_CUENTA_BLOQUEADA = (
    "Cuenta bloqueada debido a varios intentos fallidos. Inténtelo más tarde"
)
MENSAJE_ACCESO_DENEGADO = "Acceso denegado."

ROLES_INICIALES = [
    {
        "nombre": "Administrador",
        "nivel_jerarquia": NIVEL_ADMINISTRADOR,
        "descripcion": "Control total del sistema",
    },
    {
        "nombre": "Gerente de guardias",
        "nivel_jerarquia": NIVEL_SUPERVISOR,
        "descripcion": "Gestión de horarios y asignaciones",
    },
    {
        "nombre": "Supervisor",
        "nivel_jerarquia": 40,
        "descripcion": "Supervisión de personal y usuarios",
    },
    {
        "nombre": "Trabajador",
        "nivel_jerarquia": 20,
        "descripcion": "Personal administrativo u obrero",
    },
    {
        "nombre": "Funcionario",
        "nivel_jerarquia": NIVEL_OPERATIVO,
        "descripcion": "Personal de seguridad o funcionario público",
    },
]
