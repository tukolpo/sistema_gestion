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
