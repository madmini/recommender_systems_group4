from typing import List

import pandas as pd

from util.exception import MissingDataException
from util.data import Data, Column


def recommend_movies_popularity_bias(movie_id: int, n: int):
    return recommend_movies(movie_id, n, filter_below_avg_ratings=True, popularity_bias=True)


def recommend_movies_filter_avg(movie_id: int, n: int):
    return recommend_movies(movie_id, n, filter_below_avg_ratings=True)


def recommend_movies_filter_genre(movie_id: int, n: int):
    return recommend_movies_genre(movie_id, n)


def recommend_movies_filter_genre_user_bias(movie_id: int, n: int):
    return recommend_movies_genre(movie_id, n, user_bias=True)


def recommend_movies_filter_genre_popularity_bias(movie_id: int, n: int):
    return recommend_movies_genre(movie_id, n, user_bias=True, popularity_bias=True)


def recommend_movies_filter_meta(movie_id: int, n: int):
    return recommend_movie_meta(movie_id, n)


def recommend_movies(movie_id: int, n: int, filter_below_avg_ratings: bool = False, popularity_bias: bool = False) \
        -> List[int]:
    ratings = Data.ratings()

    # first get the ratings for the base movie
    ratings_of_base_movie = ratings.query('movie_id == %s' % movie_id)

    # check if there are reviews for this movie
    if ratings_of_base_movie.empty:
        raise MissingDataException('no ratings for movie_id %s' % movie_id)

    if filter_below_avg_ratings:
        # of those, select the above average ratings
        avg_rating = ratings_of_base_movie['rating'].mean()
        # query is actually faster than the python subscription syntax ( users[users['rating'] >= avg] )
        ratings_of_base_movie = ratings_of_base_movie.query('rating >= %f' % avg_rating)

    # to get ratings from all the users that have rated/liked the base movie,
    # perform a (left outer) join on all the ratings on user_id
    relevant_movies = ratings_of_base_movie.join(ratings, on='user_id', lsuffix='_L')
    # remove the columns that were duplicated as result of the join
    relevant_movies = relevant_movies[['movie_id', 'rating']]
    # remove the base movie from the results
    relevant_movies = relevant_movies.query('movie_id != %s' % movie_id)

    if relevant_movies.empty:
        raise MissingDataException('no other ratings from users that rated movie_id %s' % movie_id)

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


def recommend_movies_genre(movie_id: int, n: int, popularity_bias: bool = False, user_bias: bool = False):
    # Get similar movies based on genre
    results = get_movies_with_similar_genres(movie_id, n, popularity_bias=popularity_bias, user_bias=user_bias)
    top_n_results = results.nlargest(n)
    # export the list of movies
    results_as_list = top_n_results.index.to_list()
    # breakpoint()
    return results_as_list


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


def recommend_movie_meta(movie_id: int, n: int):
    # adult
    # color
    # genre
    # actor

    # tmdb_revenue? budget?
    # tmdb_production_countries?
    # imdb_productionCompanies?
    # directors?
    # year?

    # Get movie_meta data and set the index on movie_id
    movies_meta = Data.movie_meta()
    movies_meta = movies_meta.set_index('movielens_id')

    # Get the meta data from the base movie
    base_movie_meta = movies_meta.query('movielens_id == %s' % movie_id)

    # filtered movies based on color and adult
    filtered_movies = movies_meta.query('tmdb_adult == %s' % base_movie_meta['tmdb_adult'].iloc[0])
    filtered_movies = filtered_movies.query('imdb_color == "%s"' % base_movie_meta['imdb_color'].iloc[0])

    # filtered movies based on genre
    movies = get_movies_with_similar_genres(movie_id, n, filtered_movies)

    merged_movies = pd.merge(pd.DataFrame(movies), filtered_movies, left_index=True, right_index=True)

    # get all actors from the base movie as list
    base_actors = eval(base_movie_meta['actors'].iloc[0])

    # create a series containing the actor string and it is indexed after movie_id
    movies_actor = pd.Series(merged_movies['actors'].tolist(), index=merged_movies.index)
    # get all movie_id's where at least one actor in the base actor list is in the movie
    filtered_movies_actor = movies_actor[movies_actor.str.contains('|'.join(base_actors))]

    merged_movies = pd.merge(merged_movies, pd.DataFrame(filtered_movies_actor), left_index=True, right_index=True)

    # get the ratings/results like in recommend_movie
    ratings = Data.ratings().query('movie_id != %s' % movie_id)
    merged_ratings = pd.merge(ratings, merged_movies, left_on='movie_id', right_index=True)

    # group by movie
    ratings_grouped = merged_ratings.groupby('movie_id')
    # calculate mean rating and number of ratings for each movie
    # (select rating to remove first level of column index. before: (rating: (mean, count)), after: (mean, count) )
    measures: pd.DataFrame = ratings_grouped.agg(['mean', 'count'])['rating']
    results = measures.eval('(mean ** 3) * count')

    top_n_results = results.nlargest(n)
    # export the list of movies
    results_as_list = top_n_results.index.to_list()
    return results_as_list


