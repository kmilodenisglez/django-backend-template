from django.urls import path

from .api import LimitsAPIView

app_name = "core"

urlpatterns = [
    path("limits/", LimitsAPIView.as_view(), name="limits"),
]
