import pandas as pd

from util.data import Column, Data
from util.timer import timer


@timer
def get_movies_with_similar_genres(movie_id: int, n: int = 5, popularity_bias: bool = False
                                   , user_bias: bool = False, movies: pd.DataFrame = None):
    # Get all movies and split them into the base movie and the rest

    if n is None:
        n = 5

    # Use the preferred movie df
    if movies is None:
        all_movies = Data.movie_meta()[Column.genres.value]
    else:
        all_movies = movies[Column.genres.value]

    # get the base out of the df and remove it from the rest
    base_genres = eval(all_movies.loc[movie_id])
    all_movies = all_movies.drop(movie_id)

    # count similar genres
    all_movies = all_movies.apply(
        lambda row: count_elements_in_set(row, base_genres)
    )
    # remove all movies which have no genre in common
    filtered_movies_sum = all_movies[all_movies > 0]

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

        if popularity_bias:
            # give more weight to the number of ratings (~popularity)
            # by raising the avg ratings to some power (to preserve some notion of good vs. bad ratings)
            # and multiplying the count back in
            # additionally multiply the genre back in
            # to prevent good rated movies with little correlation to the genres
            results = measures_movies.eval('(mean ** 3) * count * genres')
        else:
            # multiply genre to prevent good rated movies with little correlation to the genres
            results = measures_movies.eval('mean * genres')
    else:
        results = filtered_movies_sum

    # breakpoint()
    return results


# function to count the elements in row which are in the base too
def count_elements_in_set(row: list, base: list):
    genres = eval(row)
    return len((set(base).intersection(genres)))
