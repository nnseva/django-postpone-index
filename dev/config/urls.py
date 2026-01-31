"""Test app URLs"""

from django.urls import re_path
from django.contrib import admin


urlpatterns = [
    re_path('admin/', admin.site.urls),
]
