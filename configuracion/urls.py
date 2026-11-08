from django.urls import path

from configuracion import views

app_name = 'configuracion'

urlpatterns = [
    path('ajustes/', views.ajustes_globales, name='ajustes_globales'),
    path('sesiones/', views.control_sesiones, name='control_sesiones'),
    path('sesiones/<str:session_key>/cerrar/', views.cerrar_sesion_admin, name='cerrar_sesion_admin'),
]