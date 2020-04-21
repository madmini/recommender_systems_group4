import pandas as pd
from typing import List

from assignment3 import recommender

# ratings.dat - UserID::MovieID::Rating::Timestamp
ratings_path: str = 'ml-1m/ratings.dat'
ratings_header = [recommender.user_id_colname, recommender.movie_id_colname, recommender.rating_colname, 'Timestamp']

# users.dat   - UserID::Gender::Age::Occupation::Zip-code
movies_path: str = 'ml-1m/movies.dat'
movies_header = [recommender.movie_id_colname, 'Title', 'Genres']

# movies.dat  - MovieID::Title::Genres
users_path: str = 'ml-1m/users.dat'
users_header = [recommender.user_id_colname, 'Gender', 'Age', 'Occupation', 'Zip-code']


def load_data_file(file_name: str, header: List[str]) -> pd.DataFrame:
    """
    load from '::' separated file.

    :param file_name: path to the data file
    :param header: list of columns to use
    :return: pandas.DataFrame from the data file
    """
    # this method is faster than the more obvious alternatives
    # assign single colon (':') as the separator, then ignore odd columns
    # this utilizes the c based scanning engine which faster by an order of magnitude
    return pd.read_csv(file_name, sep=':', usecols=range(0, 2 * len(header), 2), encoding='ansi', names=header)


def ask_user_id(user_list: List[int]) -> int:
    """
    read user_id from input. must be integer and be contained in the user_list.

    :param user_list: list of permitted user_ids.
    :return: a valid user_id
    """
    input_user_id = None

    while input_user_id is None:
        try:
            input_user_id = int(input('Enter user ID: '))

            if input_user_id not in user_list:
                print('User ID does not exist.')
                input_user_id = None

        except (ValueError, EOFError) as e:
            print('Not a valid number: ' + str(e))

    return input_user_id


def main() -> None:
    ######################## # - FETCH DATA ########################
    # load data into dataframes
    ratings = load_data_file(ratings_path, ratings_header)
    movies = load_data_file(movies_path, movies_header)

    ######################## A - INPUT USER ########################
    # read user id from console
    user_id = ask_user_id(user_list=ratings[recommender.user_id_colname])

    ######################## B - RATED MOVIES ######################
    # filter ratings by target user
    rated_movies = ratings[ratings[recommender.user_id_colname] == user_id]
    # join with movie metadata, only retain metadata and rating
    rated_meta = pd.merge(rated_movies, movies, on=recommender.movie_id_colname)[['Title', 'Genres', 'Rating']]

    # print sample (hide row numbers)
    print('Some movies this user has rated:')
    print(rated_meta.sample(15).to_string(index=False))

    ######################## C - RECOMMEND #########################
    # get recommendations
    recommendations = recommender.recommend_movies(ratings, user_id, 10)
    # join metadata, retain only metadata (the pandas.Series needs to be named in order to be joined)
    recommendations_metadata = pd.merge(recommendations, movies, on=recommender.movie_id_colname)[['Title', 'Genres']]

    # print recommendations (hide row numbers)
    print('\n\nTop 10 Recommendations:')
    print(recommendations_metadata.to_string(index=False))


main()
