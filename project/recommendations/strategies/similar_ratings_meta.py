import pandas as pd

from recommendations.strategies.shared import genre_filter
from util.data import Data, Column
from util.timer import timer


def recommend_movies_filter_meta_user(movie_id: int, n: int = 5):
    return recommend_movie_meta(movie_id, n, user_bias=True)


def recommend_movies_filter_meta_popularity(movie_id: int, n: int = 5):
    return recommend_movie_meta(movie_id, n, popularity_bias=True, user_bias=True)


@timer
def recommend_movie_meta(movie_id: int, n: int = 5, popularity_bias: bool = False, user_bias: bool = False):
    # Get movie_meta data and set the index on movie_id
    movies_meta = Data.movie_meta()
    # Get the meta data from the base movie
    base_movie_meta = movies_meta.loc[movie_id, :]

    # filtered movies based on color and adult
    filtered_movies = movies_meta.query('tmdb_adult == {}'.format(base_movie_meta['tmdb_adult']))
    filtered_movies = filtered_movies.query('imdb_color == "{}"'.format(base_movie_meta['imdb_color']))

    # filtered movies based on genre
    movies = genre_filter.get_movies_with_similar_genres(movie_id, n, movies=filtered_movies)

    # merge the number of similar genres back to the main df
    merged_movies = pd.merge(pd.DataFrame(movies), filtered_movies, left_index=True, right_index=True)
    merged_movies = merged_movies.rename(columns={"{}_x".format(Column.genres.value): Column.genres.value})

    # preparing data for the score calculation
    # count similar items in the columns or calculate the difference
    merged_movies = calculate_column(merged_movies, base_movie_meta, 'actors')
    merged_movies = calculate_column(merged_movies, base_movie_meta, 'directors')
    merged_movies = calculate_column(merged_movies, base_movie_meta, 'tmdb_keywords')
    merged_movies = calculate_column(merged_movies, base_movie_meta, 'tmdb_production_countries')
    merged_movies = calculate_column(merged_movies, base_movie_meta, 'release_year', year=True)

    # score calculation
    score = compute_score(merged_movies)

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
            results = measures_movies.eval('((mean * score) ** 3) * count')
        else:
            # multiply genre to prevent good rated movies with little correlation to the genres
            results = measures_movies.eval('mean * score')

    else:
        results = score

    return results


# function to count the elements in row which are in the base too
def count_elements_in_list(row: pd.Series, base: list, column: str):
    count = 0
    for element in base:
        if element in row[column]:
            count += 1
    return count


# function to count the elements in row which are in the base too
def count_elements_in_set(row: list, base: list):
    actors = eval(row)
    return len((set(base).intersection(actors)))


def calculate_year_value(row: int, base: int):
    if pd.isna(row):
        return 0
    diff = abs(row - base)
    if diff >= 10:
        return 0
    if diff == 0:
        return 1
    return 1 / diff


@timer
def compute_score(df: pd.DataFrame):
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

    df = df[['genres', 'actors', 'directors', 'tmdb_production_countries', 'tmdb_keywords', 'release_year']]

    # max is needed to calculate the score
    max_genre = df['genres'].max()
    max_actor = df['actors'].max()
    max_director = df['directors'].max()
    max_production_countries = df['tmdb_production_countries'].max()
    max_keywords = df['tmdb_keywords'].max()

    # for preventing divide by 0 error
    if max_keywords == 0:
        max_keywords = 1
    # for preventing divide by 0 error
    if max_director == 0:
        max_director = 1
    # for preventing divide by 0 error
    if max_production_countries == 0:
        max_production_countries = 1
    # for preventing divide by 0 error
    if max_actor == 0:
        max_actor = 1

    # calculate score between [0,100]
    # 100 if its the same movie
    # 0 if nothing is similar
    score = df['actors'] / max_actor * actor_percentage \
            + df['directors'] / max_director * directors_percentage \
            + df['release_year'] * years_percentage \
            + df['tmdb_keywords'] / max_keywords * keywords_percentage \
            + df['tmdb_production_countries'] \
            / max_production_countries * production_countries_percentage \
            + df['genres'] / max_genre * genre_percentage
    return score


@timer
def calculate_column(df: pd.DataFrame, base: pd.Series, column: str, year: bool = False):
    df_column = df[column]

    # year value is 1/abs(difference between row and base)
    # if it the difference is bigger than 10 than it is 0
    # if it is not a number it is 0 too
    # the year value is between 0 and 1
    if year:
        base = base[column]
        df_column = df_column.apply(
            lambda row: calculate_year_value(row, base)
        )
    # count how many base list items are in the row list
    else:
        base = eval(base[column])
        df_column = df_column.apply(
            lambda row: count_elements_in_set(row, base)
        )

    # merge them back and rename it (to remove the suffix "_x"
    # to select the column and merge it afterwards is faster than to work with the whole df
    # even if you only look at one column
    df = pd.merge(pd.DataFrame(df_column), df, left_index=True, right_index=True)
    df = df.rename(columns={"{}_x".format(column): column}, errors="raise")
    return df
