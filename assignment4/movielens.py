"""
adapter for the movielens dataset

provides a load function and constant column names
"""

import pandas as pd

user_id = 'UserID'
movie_id = 'MovieID'
rating = 'Rating'
rating_timestamp = 'Timestamp'
movie_title = 'Title'
movie_genres = 'Genres'
user_gender = 'Gender'
user_age = 'Age'
user_occupation = 'Occupation'
user_zip_code = 'Zip-code'

files = {
    # ratings.dat - UserID::MovieID::Rating::Timestamp
    'ratings': {
        'path': 'ml-1m/ratings.dat.xz',
        'header': [user_id, movie_id, rating, rating_timestamp],
        'index': [user_id, movie_id]
    },
    # movies.dat - MovieID::Title::Genres
    'movies': {
        'path': 'ml-1m/movies.dat',
        'header': [movie_id, movie_title, movie_genres],
        'index': movie_id
    },
    # users.dat - UserID::Gender::Age::Occupation::Zip-code
    'users': {
        'path': 'ml-1m/users.dat',
        'header': [user_id, user_gender, user_age, user_occupation, user_zip_code],
        'index': user_id
    },
}


def load_movie_genres() -> pd.DataFrame:
    # split the genre column into "boolean" columns: (put into separate dataframe for now)
    #   each genre becomes a new column, with a value of 1 if the movie has the respective genre, and 0 if not
    return load_movies().pop(movie_genres).str.get_dummies(sep='|')


def load_movies(use_genre_bitset: bool = False) -> pd.DataFrame:
    # using ansi (Windows CP-1252) encoding
    # use index to avoid duplicate/unnecessary indexing, as the datafiles already have primary keys
    return pd.read_csv('ml-1m/movies.dat', sep='::', engine='python', encoding='ansi',
                       names=[movie_id, movie_title, movie_genres], index_col=movie_id)


def load_ratings() -> pd.DataFrame:
    # this method is faster than the more obvious alternatives
    #   assign single ':' as the separator, then ignore odd columns with usecols=<even numbers>
    #   this utilizes the c based scanning engine which faster by an order of magnitude
    #   this is not applicable for the movies file, as its title column contains colons
    # using ansi (Windows CP-1252) encoding
    df: pd.DataFrame = pd.read_csv('ml-1m/ratings.dat.xz', sep=':', encoding='ansi',
                                   usecols=[0, 2, 4, 6], names=[user_id, movie_id, rating, rating_timestamp])

    # use index to avoid duplicate/unnecessary indexing, as the datafiles already have primary keys
    # Note: read_csv has an option for this, however apparently uses unstable APIs when generating a multi-index
    df.set_index(keys=[user_id, movie_id], inplace=True)

    return df
