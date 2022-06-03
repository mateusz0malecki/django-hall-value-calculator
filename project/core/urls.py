from django.contrib import admin
from django.urls import path, include

from api import urls as api_urls

from rest_framework.authtoken import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urls)),
    path('auth/', views.obtain_auth_token)
]
