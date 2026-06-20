from core.settings import *

INSTALLED_APPS = [
    *INSTALLED_APPS,
    "trabajadores_ext",
]

MIDDLEWARE = [
    *MIDDLEWARE[:7],
    "trabajadores_ext.middleware.AuditoriaTrabajadorMiddleware",
    *MIDDLEWARE[7:],
]

ROOT_URLCONF = "core.urls_extensions"
