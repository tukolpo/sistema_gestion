from django.urls import path
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

from usuarios.serializers import EmailTokenObtainPairSerializer
from usuarios.api_views import PerfilAPIView


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


urlpatterns = [
    path("login/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("login/logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("perfil/", PerfilAPIView.as_view(), name="api_perfil"),
]
