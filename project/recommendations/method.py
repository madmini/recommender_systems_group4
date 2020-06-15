from enum import Enum
from typing import Callable

import pandas as pd

from recommendations.filters.collection import CollectionFilter
from recommendations.filters.popularity import PopularityBias
from recommendations.strategies import users_who_enjoy_this_also_like, cast_and_crew, common_genres, meta_mix
from recommendations.strategies.dummy import reference, dummy, sequel
from recommendations.strategies.hybrid.combined import Combined
from recommendations.strategies.hybrid.slot_based import SlotBased
from recommendations.strategies.shared import relevance_helper
from recommendations.strategies.tf_idf import TfIdfSimilarity
from util.data import Column


class Method(Enum):
    # dummy = ('dummy', dummy.sample)
    reference = ('TMDb Recommendations Reference', reference.tmdb_reference)
    sequels = ('Sequels', sequel.sequels)

    # ADD METHODS HERE
    # internal_method_name = ('Display Name', package.method_name)
    # Note: if a method has the same internal name as an imported package, its name will hide the package name

    # similar user ratings
    # similarity_movies = (
    #     'Combined(Keywords, Genres, Actors, Directors, Year)',
    #     similiar_movies.recommend_movies
    # )
    # similar_ratings_plain = (
    #     'Similar User Ratings',
    #     users_who_enjoy_this_also_like.recommend_movies
    # )
    similar_ratings_above_avg = (
        'Users who liked this also liked',
        users_who_enjoy_this_also_like.recommend_movies_filter_avg
    )
    similar_ratings_pop_bias = (
        'Users who liked this also liked (with popularity bias)',
        PopularityBias(users_who_enjoy_this_also_like.recommend_movies_filter_avg)
    )
    # similar_ratings_pop = (
    #     'Similar User Ratings + Popularity Bias',
    #     users_who_enjoy_this_also_like.recommend_movies_popularity_bias
    # )
    similarity_ml = (
        'TF-IDF keywords',
        TfIdfSimilarity(Column.keywords)
    )
    # similarity_ml2 = (
    #     'ML Summary',
    #     TfIdfSimilarity(Column.summary)
    # )
    # similar_rating_genre = (
    #     'Similar Genres Rating',
    #     common_genres.recommend_movies_filter_genre
    # )
    # similar_rating_genre_user = (
    #     'Similar Genres Rating + User Bias',
    #     common_genres.recommend_movies_filter_genre_user_bias
    # )
    similar_rating_genre_pop = (
        'Genres + Ratings (with popularity bias)',
        common_genres.recommend_movies_filter_genre_popularity_bias
    )
    similar_rating_meta_plain = (
        'Meta-Mix',
        meta_mix.recommend_movie_meta
    )
    # similar_rating_meta_user = (
    #     'Similarity based on Meta-data + User Bias',
    #     meta_mix.recommend_movies_filter_meta_user
    # )
    # similar_rating_meta_pop = (
    #     'Similarity based on Meta-data + User Bias + Popularity Bias',
    #     meta_mix.recommend_movies_filter_meta_popularity
    # )
    # same_actors = (
    #     'Cast',
    #     cast_and_crew.same_actors
    # )
    # same_directors = (
    #     'Directors',
    #     cast_and_crew.same_directors
    # )
    # slot_based_test = (
    #     'Slots',
    #     SlotBased([common_genres.recommend_movies_filter_genre_popularity_bias, cast_and_crew.same_actors,
    #                cast_and_crew.same_directors], [2, 2, 2])
    # )
    combined_test = (
        'First direct sequel + (genres & actors & directors & users)',
        SlotBased(
            [
                sequel.sequels,
                PopularityBias(CollectionFilter(
                    Combined(
                        [
                            common_genres.recommend_movies_filter_genre_user_bias,
                            cast_and_crew.same_actors,
                            cast_and_crew.same_directors,
                            users_who_enjoy_this_also_like.recommend_movies_filter_avg
                        ],
                        [2, 1, 1, 3]
                    )
                ))
            ],
            [1, 10]
        )
    )
    # combined_similar_movies_nosummary_notnormalized = (
    #     'similar movies - no summary -not normalized',
    #     Combined([TfIdfSimilarity(Column.keywords),
    #               cast_and_crew.same_actors, cast_and_crew.same_directors,
    #               relevance_helper.get_genre_overlap_values, relevance_helper.get_year_relevance],
    #              [1.0, 0.1, 0.1, 0.8, 0.05], normalize=False)
    # )
    # combined_similar_movies_nosummary = (
    #     'similar movies - no summary',
    #     Combined([TfIdfSimilarity(Column.keywords),
    #               cast_and_crew.same_actors, cast_and_crew.same_directors,
    #               relevance_helper.get_genre_overlap_values, relevance_helper.get_year_relevance],
    #              [1.0, 0.1, 0.1, 0.8, 0.05])
    # )
    combined_all_columns = (
        'TF-IDF + Crew + Genres + Release Year',
        Combined([TfIdfSimilarity(Column.keywords), TfIdfSimilarity(Column.summary),
                  cast_and_crew.same_actors, cast_and_crew.same_directors,
                  relevance_helper.get_genre_overlap_values, relevance_helper.get_year_relevance],
                 [9, 7, 4, 2, 6, 1])
    )
    combined_all_columns_bias = (
        'TF-IDF + Crew + Genres + Release Year (with popularity bias)',
        PopularityBias(combined_all_columns[1], score_weight=2)
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
