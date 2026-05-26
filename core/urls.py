from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenBlacklistView,
)

from usuarios.api_views import PerfilAPIView
from usuarios.serializers import EmailTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "api/auth/login/logout/", TokenBlacklistView.as_view(), name="token_blacklist"
    ),
    path("api/auth/perfil/", PerfilAPIView.as_view(), name="api_perfil"),
    path("", include("usuarios.urls", namespace="usuarios")),
]
