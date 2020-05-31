from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('django_app_fancy.urls')),
    path('old/', include('django_app_old.urls')),
    path('admin/', admin.site.urls),
]
