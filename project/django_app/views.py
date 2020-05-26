from django.http import Http404
from django.shortcuts import render, redirect

from recommendations.adapter import *
from util.exception import MovieNotFoundException, MethodNotFoundException, MissingDataException


def search(request):
    if 'method' in request.session:
        method = request.session['method']
    else:
        method = Method.default().as_dict()
        request.session['method'] = method

    context = {
        'conf': {
            'immediate_method_change': False
        },
        'current_method': method,
        'methods': get_methods(),
    }

    return render(request, 'movie/search.html', context)


def display_similar(request, movie_id: int, method: str = None):
    if method is None:
        if 'method' in request.session:
            method = request.session['method']
        else:
            method = Method.default().name
            request.session['method'] = method

    try:
        movie = get_movie_data(movie_id)[0]
        recommendations = recommend_movies(movie_id, 5, method_name=method)

    except MovieNotFoundException:
        raise Http404("We do not have data on a movie with ID %s." % movie_id)

    except MethodNotFoundException:
        raise Http404("There is no method %s." % method)

    except MissingDataException as e:
        raise Http404("Missing data: %s" % e.args[0])

    context = {
        'conf': {
            'immediate_method_change': True
        },
        'current_method': method,
        'methods': get_methods(),
        'base_movie': movie,
        'recommendations': recommendations
    }

    return render(request, 'movie/list.html', context)


def redirect_main(request):
    return redirect('search')  # , permanent=True)


def search_post(request):
    return redirect(
        'display_similar',
        movie_id=request.POST.get('movie'),
        method=request.POST.get('method'),
    )
