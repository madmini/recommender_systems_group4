from django.shortcuts import render, redirect

# Create your views here.
from recommendations.adapter import recommend_movies, get_methods
from recommendations.method import Method
from util.search import Search


def redirect_main(request):
    return redirect('test')


def recommend(request, movie_id: int, method_name: str = None):
    if method_name is not None:
        request.session['method'] = method_name
    else:
        if 'method' in request.session:
            method_name = request.session['method']
        else:
            method_name = Method.default().name
            request.session['method'] = method_name

        return redirect('recommend', movie_id=movie_id, method_name=method_name)

    movies = recommend_movies(movie_id=movie_id, n=5, method_name=method_name)

    return render(request, 'movie/recommendations.html', context={
        'mode': 'recommend',
        'movies': movies,
        'methods': get_methods(method_name),
        'dark_theme': True,
        'load_static': True,
    })


def search(request, query: str = None):
    if query is None:
        return redirect('search', query=request.POST.get('search'))

    movies = Search.search(query, 25)

    return render(request, 'movie/recommendations.html', context={
        'mode': 'search',
        'search_query': query,
        'movies': movies,
        'dark_theme': True,
        'load_static': True,
    })


def test(request):
    request.session['method'] = 'dummy'
    if 'method' in request.session:
        method = request.session['method']
    else:
        method = Method.default().name
        request.session['method'] = method

    movies = recommend_movies(movie_id=1, n=5, method_name='dummy')

    return render(request, 'movie/recommendations.html', context={
        'movies': movies,
        'dark_theme': True,
        'load_static': True,
        'methods': get_methods(method),
    })
