from django.urls import path
from . import views

app_name = "vacaciones"

urlpatterns = [
    path("", views.gestion_vacaciones, name="gestion_vacaciones"),
]