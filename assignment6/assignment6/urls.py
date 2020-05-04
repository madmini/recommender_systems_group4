from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('id_selector.urls')),
    path('recommender/', include('recommender.urls')),
    path('admin/', admin.site.urls),
]
