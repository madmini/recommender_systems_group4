from typing import List

import pandas as pd

from util.exception import MissingDataException
from util.data import Data


def recommend_movies_popularity_bias(movie_id: int, n: int):
    return recommend_movies(movie_id, n, filter_below_avg_ratings=True, popularity_bias=True)


def recommend_movies_filter_avg(movie_id: int, n: int):
    return recommend_movies(movie_id, n, filter_below_avg_ratings=True)


def recommend_movies(movie_id: int, n: int, filter_below_avg_ratings: bool = False, popularity_bias: bool = False) \
        -> List[int]:
    ratings = Data.ratings()

    # first get the ratings for the base movie
    ratings_of_base_movie = ratings.query('movie_id == %s' % movie_id)
    if ratings_of_base_movie.empty:
        raise MissingDataException('no ratings for movie_id %s' % movie_id)

    if filter_below_avg_ratings:
        # of those, select the above average ratings
        avg_rating = ratings_of_base_movie['rating'].mean()

        print(ratings_of_base_movie)
        print(ratings_of_base_movie['rating'].unique())
        print(avg_rating)

        # query is actually faster than the python subscription syntax ( users[users['rating'] >= avg] )
        ratings_of_base_movie = ratings_of_base_movie.query('rating >= %f' % avg_rating)

    # to get ratings from all the users that have rated/liked the base movie,
    # perform a (left outer) join on all the ratings on user_id
    relevant_movies = ratings_of_base_movie.join(ratings, on='user_id', lsuffix='_L')
    # remove the columns that were duplicated as result of the join
    relevant_movies = relevant_movies[['movie_id', 'rating']]
    # remove the base movie from the results
    relevant_movies = relevant_movies.query('movie_id != %s' % movie_id)

    # group by movie
    relevant_movie_groups = relevant_movies.groupby('movie_id')
    # calculate mean rating and number of ratings for each movie
    # (select rating to remove first level of column index. before: (rating: (mean, count)), after: (mean, count) )
    measures: pd.DataFrame = relevant_movie_groups.agg(['mean', 'count'])['rating']

    if popularity_bias:
        # give more weight to the number of ratings (~popularity)
        # by raising the avg ratings to some power (to preserve some notion of good vs. bad ratings)
        # and multiplying the count back in
        results = measures.eval('(mean ** 3) * count')
    else:
        results = measures['mean']

    # select the best results (nlargest is significantly faster than sort+head for small n)
    top_n_results = results.nlargest(n)
    # export the list of movies
    results_as_list = top_n_results.index.to_list()

    return results_as_list
