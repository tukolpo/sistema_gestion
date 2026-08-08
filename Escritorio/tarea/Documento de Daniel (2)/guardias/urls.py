from django.urls import path
from . import views

app_name = 'guardias'

urlpatterns = [
    path('asignar/', views.asignar_turno, name='asignar_turno'),
    path('cronograma/', views.cronograma_semanal, name='cronograma_semanal'),
    path('cronograma/<int:cronograma_id>/aprobar/', views.aprobar_cronograma, name='aprobar_cronograma'),
]
