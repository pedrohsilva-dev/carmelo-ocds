from django.contrib import admin
from django.urls import include, path
from django.conf.urls import handler400, handler403, handler404, handler500

from core import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("administrador/", admin.site.urls),
    path("contas/", include("accounts.urls")),
    path("membros/", include("members.urls")),
    path("carmelo/", include("carmel.urls")),
]

urlpatterns += static(
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT,
)


handler400 = "base.views.error400"
handler403 = "base.views.error403"
handler404 = "base.views.error404"
handler500 = "base.views.error500"
