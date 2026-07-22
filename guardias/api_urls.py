from django.urls import path

from guardias.api_views import DisponibilidadAPIView

urlpatterns = [
    path("disponibilidad/", DisponibilidadAPIView.as_view(), name="disponibilidad"),
]
