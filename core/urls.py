from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "api/auth/login/logout/", TokenBlacklistView.as_view(), name="token_blacklist"
    ),
    path("", include("usuarios.urls", namespace="usuarios")),
]
