from enum import Enum
from typing import Callable

import pandas as pd

from recommendations.strategies import users_who_enjoy_this_also_like, similarity_ml, cast_and_crew, \
    similar_ratings_genre, similar_ratings_meta, similiar_movies
from recommendations.strategies.dummy import reference, dummy, sequel


class Method(Enum):
    dummy = ('dummy', dummy.sample)
    reference = ('TMDb Recommendations Reference', reference.tmdb_reference)
    sequels = ('Sequels', sequel.sequels)

    # ADD METHODS HERE
    # internal_method_name = ('Display Name', package.method_name)
    # Note: if a method has the same internal name as an imported package, its name will hide the package name

    # similar user ratings
    similarity_movies = (
        'Combined(Keywords, Genres, Actors, Directors, Year)',
        similiar_movies.recommend_movies
    )
    similar_ratings_plain = (
        'Similar User Ratings',
        users_who_enjoy_this_also_like.recommend_movies
    )
    similar_ratings_above_avg = (
        'Similar above-avg User Ratings',
        users_who_enjoy_this_also_like.recommend_movies_filter_avg
    )
    similar_ratings_pop = (
        'Similar User Ratings + Popularity Bias',
        users_who_enjoy_this_also_like.recommend_movies_popularity_bias
    )
    similarity_ml = (
        'ML',
        similarity_ml.TfIdfSimilarity.recommend
    )
    similar_rating_genre = (
        'Similar Genres Rating',
        similar_ratings_genre.recommend_movies_filter_genre
    )
    similar_rating_genre_user = (
        'Similar Genres Rating + User Bias',
        similar_ratings_genre.recommend_movies_filter_genre_user_bias
    )
    similar_rating_genre_pop = (
        'Similar Genres Rating + User Bias + Popularity Bias',
        similar_ratings_genre.recommend_movies_filter_genre_popularity_bias
    )
    similar_rating_meta_plain = (
        'Similarity based on Meta-data',
        similar_ratings_meta.recommend_movie_meta
    )
    similar_rating_meta_user = (
        'Similarity based on Meta-data + User Bias',
        similar_ratings_meta.recommend_movies_filter_meta_user
    )
    similar_rating_meta_pop = (
        'Similarity based on Meta-data + User Bias + Popularity Bias',
        similar_ratings_meta.recommend_movies_filter_meta_popularity
    )
    same_actors = (
        'Cast',
        cast_and_crew.same_actors
    )
    same_directors = (
        'Directors',
        cast_and_crew.same_directors
    )

    def __init__(self, name: str, method: Callable[[int], pd.Series]):
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

    @classmethod
    def default(cls):
        return cls.dummy