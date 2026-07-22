from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
   path("api/trabajadores/", include("trabajadores.api_urls")),
    path("api/trabajadores/", include("trabajadores_ext.api_urls")),
    path("trabajadores/", include("trabajadores.urls", namespace="trabajadores")),
    path("trabajadores/", include("trabajadores_ext.urls", namespace="trabajadores_ext")),
    path("", include("usuarios.urls", namespace="usuarios")),
    path("api/guardias/", include("guardias.api_urls")),
    path("guardias/", include("guardias.urls")),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
