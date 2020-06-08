from typing import List
import pandas as pd

from recommendations import genre_filter

from util.exception import MissingDataException
from util.data import Data, Column


def recommend_movies_filter_meta(movie_id: int, n: int):
    return recommend_movie_meta(movie_id, n)


def recommend_movies_filter_meta_user(movie_id: int, n: int):
    return recommend_movie_meta(movie_id, n, user_bias=True)


def recommend_movies_filter_meta_popularity(movie_id: int, n: int):
    return recommend_movie_meta(movie_id, n, popularity_bias=True, user_bias=True)


def recommend_movie_meta(movie_id: int, n: int, popularity_bias: bool = False, user_bias: bool = False):
    # adult
    # color

    # genre
    genre_percentage = 35
    # actor
    actor_percentage = 20
    # directors
    directors_percentage = 8
    # keywords
    keywords_percentage = 20
    # years
    years_percentage = 10
    # production_countries
    production_countries_percentage = 7


    # Get movie_meta data and set the index on movie_id
    movies_meta = Data.movie_meta()
    movies_meta = movies_meta.set_index('movielens_id')

    # Get the meta data from the base movie
    base_movie_meta = movies_meta.query('movielens_id == %s' % movie_id)

    # filtered movies based on color and adult
    filtered_movies = movies_meta.query('tmdb_adult == %s' % base_movie_meta['tmdb_adult'].iloc[0])
    filtered_movies = filtered_movies.query('imdb_color == "%s"' % base_movie_meta['imdb_color'].iloc[0])

    # filtered movies based on genre
    movies = genre_filter.get_movies_with_similar_genres(movie_id, n, filtered_movies)

    merged_movies = pd.merge(pd.DataFrame(movies), filtered_movies, left_index=True, right_index=True)

    # needed to calculate score: genre_count / max * genre_percentage
    max_genre = merged_movies[0].max()

    # transform string into list and count the actors which are in the base and the rows
    base_actors = eval(base_movie_meta['actors'].iloc[0])
    merged_movies['actors'] = merged_movies['actors'].tolist()
    merged_movies['actor_count'] = merged_movies.apply(lambda row:
                                                       count_elements_in_list(row, base_actors, 'actors')
                                                       , axis=1)

    # needed to calculate score: actor_count / max * actor_percentage
    max_actor = merged_movies['actor_count'].max()

    # for preventing divide by 0 error
    if max_actor == 0:
        max_actor = 1

    # same as actors for directors
    base_directors = eval(base_movie_meta['directors'].iloc[0])
    merged_movies['directors'] = merged_movies['directors'].tolist()
    merged_movies['director_count'] = merged_movies.apply(lambda row:
                                                          count_elements_in_list(row, base_directors, 'directors')
                                                          , axis=1)

    # needed to calculate score: director_count / max * director_percentage
    max_director = merged_movies['director_count'].max()

    # for preventing divide by 0 error
    if max_director == 0:
        max_director = 1

    # calculating year difference, result is normally between [-infinity,1]
    # 1 if it has the same year
    # below 0 if the difference is more than base year * 2
    merged_movies['year_difference'] \
        = (base_movie_meta['release_year'].iloc[0]
           - abs(merged_movies['release_year'] - base_movie_meta['release_year'].iloc[0])) \
          / base_movie_meta['release_year'].iloc[0]

    # same as actors for production countries
    base_production_countries = eval(base_movie_meta['tmdb_production_countries'].iloc[0])
    merged_movies['tmdb_production_countries'] = merged_movies['tmdb_production_countries'].tolist()
    merged_movies['tmdb_production_countries_count'] \
        = merged_movies.apply(lambda row:
                              count_elements_in_list(row, base_production_countries, 'tmdb_production_countries')
                              , axis=1)

    # needed to calculate score: production_countries_count / max * production_countries_percentage
    max_production_countries = merged_movies['tmdb_production_countries_count'].max()

    # for preventing divide by 0 error
    if max_production_countries == 0:
        max_production_countries = 1

    # same as actors for keywords
    base_keywords = eval(base_movie_meta['tmdb_keywords'].iloc[0])
    merged_movies['tmdb_keywords'] = merged_movies['tmdb_keywords'].tolist()
    merged_movies['tmdb_keywords_count'] = merged_movies.apply(lambda row:
                                                          count_elements_in_list(row, base_keywords, 'tmdb_keywords')
                                                          , axis=1)

    # needed to calculate score: keywords_count / max * keywords_percentage
    max_keywords = merged_movies['tmdb_keywords_count'].max()

    # for preventing divide by 0 error
    if max_keywords == 0:
        max_keywords = 1

    # calculate score between [0,100]
    # 100 if its the same movie
    # 0 if nothing is similar
    # below 0 if the year difference is too damn high xD
    score = merged_movies['actor_count'] / max_actor * actor_percentage\
            + merged_movies['director_count'] / max_director * directors_percentage\
            + merged_movies['year_difference'] * years_percentage\
            + merged_movies['tmdb_keywords_count'] / max_keywords * keywords_percentage\
            + merged_movies['tmdb_production_countries_count'] / max_production_countries * production_countries_percentage\
            + merged_movies[0] / max_genre * genre_percentage

    # calculate the ranking with the avg user rating
    if user_bias:
        # get the ratings/results like in recommend_movie
        ratings = Data.ratings().query('movie_id != %s' % movie_id)
        merged_ratings = pd.merge(ratings, merged_movies, left_on='movie_id', right_index=True)

        # group by movie
        ratings_grouped = merged_ratings.groupby('movie_id')
        # calculate mean rating and number of ratings for each movie
        # (select rating to remove first level of column index. before: (rating: (mean, count)), after: (mean, count) )
        measures: pd.DataFrame = ratings_grouped.agg(['mean', 'count'])['rating']

        # merging mean, count and genre sum into one DataFrame
        measures_movies = pd.merge(measures, pd.DataFrame(score), left_index=True, right_index=True)
        measures_movies = measures_movies.rename(columns={0: 'score'})

        # additionally calculate it with the popularity of the movies
        if popularity_bias:
            # give more weight to the number of ratings (~popularity)
            # by raising the avg ratings to some power (to preserve some notion of good vs. bad ratings)
            # and multiplying the count back in
            # additionally multiply the genre back in
            # to prevent good rated movies with little correlation to the genres
            results = measures_movies.eval('(mean ** 3) * count * score')
        else:
            # multiply genre to prevent good rated movies with little correlation to the genres
            results = measures_movies.eval('mean * score')

    else:
        results = score

    top_n_results = results.nlargest(n)
    # export the list of movies
    results_as_list = top_n_results.index.to_list()
    breakpoint()
    return results_as_list


# function to count the elements in row which are in the base too
def count_elements_in_list(row: pd.Series, base: list, column: str):
    count = 0
    for element in base:
        if element in row[column]:
            count += 1
    return count
