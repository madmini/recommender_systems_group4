from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='id_selector/index'),
    path('get_user_id', views.get_user_id, name='id_selector/get_user_id'),
    path('recommend_movies', views.recommend_movies, name='id_selector/recommend_movies')
]
