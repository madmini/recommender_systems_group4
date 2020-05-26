from typing import List

import pandas as pd

from util.data import Data


def recommend_movies(movie_id: int, n: int) -> List[int]:
    # ratings with MultiIndex(user, movie)
    ratings: pd.DataFrame = Data.ratings().reset_index()

    # to get all the users that have rated the movie,
    # swap the levels of the MultiIndex so that it now looks like (movie, user)
    users_that_rated_the_base_movie: pd.DataFrame = ratings  # .swaplevel(0, 1)
    # then just select the movie by its id
    users_that_rated_the_base_movie = users_that_rated_the_base_movie.query(
        'movie_id == %d' % movie_id)  # .loc[movie_id]

    # of those, select the above average ratings
    avg_rating = users_that_rated_the_base_movie['rating'].mean()
    # query is actually faster than the python subscription syntax ( users[users['rating'] >= avg] )
    users_that_liked_the_base_movie: pd.DataFrame = users_that_rated_the_base_movie.query('rating >= %f' % avg_rating)

    # to get all the ratings from all the users that have rated the movie,
    # perform a (left outer) join back on the full ratings dataframe,
    relevant_movies = pd.merge(users_that_liked_the_base_movie, ratings, on='user_id', how='left', suffixes=('_L', ''))

    relevant_movies.set_index('movie_id', inplace=True)
    # remove the base movie from the results
    relevant_movies = relevant_movies.query('movie_id != %d' % movie_id)  # , level='movie_id')
    # then drop the 'ratingl' column (contains the rating for the base movie for every user)
    relevant_movies = relevant_movies['rating']

    # group by movie
    relevant_movie_groups = relevant_movies.groupby('movie_id')
    # aggregate
    measures: pd.DataFrame = relevant_movie_groups.agg(['mean', 'count'])

    # apply bias towards movies with more reviews for better accuracy (popularity bias)
    measures.eval('corrected = (mean ** 3) * count', inplace=True)
    # sort (.nlargest() is faster for small n)
    results: pd.DataFrame = measures.nlargest(n, 'corrected')

    return results.index.to_list()


# print(recommend_movies(123, 5))
