from django.shortcuts import redirect
from django.urls import path

from . import views

urlpatterns = [
    path('', views.redirect_main),
    path(
        'similar/',
        views.search_post,
        name='search_post'
    ),

    path('search/', views.search, name='search'),
    path('similar/<int:movie_id>/<str:method>', views.display_similar, name='display_similar'),
]
