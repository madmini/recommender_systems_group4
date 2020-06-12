import functools
from enum import Enum
from typing import List, Dict, Callable

from recommendations import dummy, reference, \
    similar_ratings_user, similarity_ml, similar_ratings_meta, similar_ratings_genre, same_actors, all
from util.data_helper import get_movie_meta_for
from util.exception import MethodNotFoundException


class Method(Enum):
    dummy = ('dummy', dummy.recommend_movies)
    all = ('all', all.recommend_movies)
    reference = ('TMDb Recommendations Reference', reference.recommend_movies)

    # ADD METHODS HERE
    # internal_method_name = ('Display Name', package.method_name)
    # Note: if a method has the same internal name as an imported package, its name will hide the package name

    # similar user ratings
    similar_ratings_plain = ('Similar User Ratings', similar_ratings_user.recommend_movies)
    similar_ratings_above_avg = ('Similar above-avg User Ratings', similar_ratings_user.recommend_movies_filter_avg)
    similar_ratings_pop = ('Similar User Ratings + Popularity Bias', similar_ratings_user.recommend_movies_popularity_bias)
    similarity_ml = ('ML', similarity_ml.recommend_movies)
    similar_rating_genre = ('Similar Genres Rating', similar_ratings_genre.recommend_movies_filter_genre)
    similar_rating_genre_user = ('Similar Genres Rating + User Bias'
                                 , similar_ratings_genre.recommend_movies_filter_genre_user_bias)
    similar_rating_genre_pop = ('Similar Genres Rating + User Bias + Popularity Bias'
                                , similar_ratings_genre.recommend_movies_filter_genre_popularity_bias)
    similar_rating_meta_plain = ('Similarity based on Meta-data'
                                 , similar_ratings_meta.recommend_movies_filter_meta)
    similar_rating_meta_user = ('Similarity based on Meta-data + User Bias'
                                , similar_ratings_meta.recommend_movies_filter_meta_user)
    similar_rating_meta_pop = ('Similarity based on Meta-data + User Bias + Popularity Bias'
                               , similar_ratings_meta.recommend_movies_filter_meta_popularity)
    same_actors = ('Cast', same_actors.recommend_movies)

    @classmethod
    def default(cls):
        return cls.dummy

    def __init__(self, name: str, method: Callable[[int, int], List[int]]):
        # note: the field 'name' is reserved for enums
        self.display_name = name
        self.method = method

    def __call__(self, *args, **kwargs):
        return self.method(*args, **kwargs)

    def __str__(self):
        return self.name

    def as_dict(self):
        return {
            'name': self.name,
            'display_name': self.display_name
        }


# @functools.lru_cache(maxsize=None, typed=False)
def _recommend_movies(movie_id: int, n: int, method: Method) -> List[Dict]:
    recommendations: List[int] = [movie_id]
    recommendations.extend(method(movie_id, n))

    return get_movie_meta_for(recommendations)


def recommend_movies(movie_id: int, n: int, method_name: str = None, method: Method = None):
    if method is None:
        if method_name is None or method_name not in Method.__members__:
            raise MethodNotFoundException(method_name)
        method = Method[method_name]

    return _recommend_movies(movie_id, n, method)


def get_methods(active_method: str = None) -> List[Dict[str, str]]:
    methods = list()
    for method in Method:
        method_dict = method.as_dict()
        if method.name == active_method or method == active_method:
            method_dict['active'] = True
        methods.append(method_dict)

    return methods
