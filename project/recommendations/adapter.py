from typing import List, Dict

from pandas import Series

from recommendations.filters.history import History
from recommendations.method import Method
from util.data_helper import get_movie_meta_for
from util.exception import MethodNotFoundException


# @functools.lru_cache(maxsize=None, typed=False)
def _recommend_movies(movie_id: int, n: int, method: Method) -> List[Dict]:
    # start with the movie itself
    movies: List[int] = [movie_id]

    # calculate similarities
    scores: Series = method(movie_id)
    # and filter out any movies that were recommended recently
    scores = History.filter(scores)

    # movies = [base_movie, ...recommendations]
    movies.extend(scores.nlargest(n).index)
    # add recommendations for movies
    History.append(movies)

    return get_movie_meta_for(movies)


def recommend_movies(movie_id: int, n: int, method_name: str = None, method: Method = None):
    """ wrapper to select the right method """
    if method is None:
        if method_name is None or method_name not in Method.__members__:
            raise MethodNotFoundException(method_name)
        method = Method[method_name]

    return _recommend_movies(movie_id, n, method)


def get_methods(active_method: str = None) -> List[Dict[str, str]]:
    """ get a list of available methods (recommendation strategies) """
    methods = list()
    for method in Method:
        method_dict = method.as_dict()
        if method.name == active_method or method == active_method:
            method_dict['active'] = True
        methods.append(method_dict)
    return methods
