from typing import List

import pandas as pd

from util.exception import MissingDataException
from util.data import Data, Column


def get_movies_with_similar_genres(movie_id: int, n: int, popularity_bias: bool = False
                                   , user_bias: bool = False, movies: pd.DataFrame = None):
    # Get all movies and split them into the base movie and the rest
    if movies is None:
        movies = Data.movies()

    other_movies = movies.query('movie_id != %s' % movie_id)
    base_movie = movies.query('movie_id == %s' % movie_id)

    # extract the different genres from the base movie
    base_movie_genres = base_movie[str(Column.genres)].str.get_dummies(sep='|')

    # extend other_movies with bool columns representing the genres (1 has the genre, 0 not)
    # furthermore the title and genres columns are removed and the movie_id is an index instead of column
    movies_with_genres = pd.concat([other_movies, other_movies[str(Column.genres)].str.get_dummies(sep='|')], axis=1)
    movies_with_genres = movies_with_genres.drop(columns=[str(Column.title), str(Column.genres)])
    movies_with_genres = movies_with_genres.set_index(str(Column.movie_id))

    # removes all column which are not in the base movie
    filtered_movies = movies_with_genres.loc[:, base_movie_genres.columns.values.tolist()]

    # sum up all columns to get the number of fitting genres
    filtered_movies_sum = filtered_movies.sum(axis='columns')
    # remove all movies which have no genre in common
    filtered_movies_sum = filtered_movies_sum[filtered_movies_sum > 0]

    # if user_bias is true
    if user_bias:
        # reduce the amount of movies to n * 10 movies
        top_n_mul_ten = filtered_movies_sum.nlargest(n * 10)
        ratings = Data.ratings()

        # group by movie
        ratings_grouped = ratings.groupby(str(Column.movie_id))
        # calculate mean rating and number of ratings for each movie
        # (select rating to remove first level of column index. before: (rating: (mean, count)), after: (mean, count) )
        measures: pd.DataFrame = ratings_grouped.agg(['mean', 'count'])[str(Column.rating)]

        # merging mean, count and genre sum into one DataFrame
        measures_movies = pd.merge(measures, pd.DataFrame(top_n_mul_ten), left_index=True, right_index=True)
        measures_movies = measures_movies.rename(columns={0: 'genre'})

        if popularity_bias:
            # give more weight to the number of ratings (~popularity)
            # by raising the avg ratings to some power (to preserve some notion of good vs. bad ratings)
            # and multiplying the count back in
            # additionally multiply the genre back in
            # to prevent good rated movies with little correlation to the genres
            results = measures_movies.eval('(mean ** 3) * count * genre')
        else:
            # multiply genre to prevent good rated movies with little correlation to the genres
            results = measures_movies.eval('mean * genre')
    else:
        results = filtered_movies_sum

    # breakpoint()
    return results