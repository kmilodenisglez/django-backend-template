"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

# optional: redirect bare root "/" to default language root (uncomment if wanted)
# urlpatterns = [path('', RedirectView.as_view(url=f'/{settings.LANGUAGE_CODE}/', permanent=False))]

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),  # language switcher endpoints
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("accounts/", include("allauth.urls")),
]

# Put your app and admin routes inside i18n_patterns so they accept /<lang>/...
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path(
        "subscriptions/", include("apps.subscriptions.urls", namespace="subscriptions")
    ),
)

# API endpoints for core
urlpatterns += [
    path("api/core/", include("apps.core.urls", namespace="core")),
    # App-level API router (apps)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
