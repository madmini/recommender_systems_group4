from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='recommender/index'),
    path('home', views.home, name='recommender/home'),
]
