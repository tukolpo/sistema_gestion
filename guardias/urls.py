from django.urls import path
from . import views

app_name = "guardias"

urlpatterns = [
    path("", views.gestion_guardias, name="gestion_guardias"),
]