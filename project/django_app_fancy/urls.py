from django.shortcuts import redirect
from django.urls import path

from . import views

urlpatterns = [
    path('', views.redirect_main),

    path('find/<str:query>', views.search, name='search'),
    path('find/', views.search, name='search_empty'),

    path('movie/<int:movie_id>/method/<str:method_name>', views.recommend, name='recommend'),
    path('movie/<int:movie_id>', views.recommend, name='recommend_default'),

    path('test/', views.test, name='test'),
]
