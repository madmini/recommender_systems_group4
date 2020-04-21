import pandas as pd
from typing import List

import movielens as ml
from recommender import Recommender


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

        except ValueError as e:
            print('Not a valid number: ' + str(e))

    return input_user_id


def print_user_ratings(ratings, movies, user_id):
    print('\nRatings of user ' + str(user_id) + ':\n')
    print(pd.merge(ratings.loc[user_id][ml.rating], movies, how='left', left_index=True, right_index=True).sort_values(
        by=ml.rating, ascending=False).to_string())
    # print(ratings.loc[user_id][ml.rating].count())


def print_recommendations(recommendations):
    print('\n\nTop ' + str(recommendations.count()) + ' recommendations:\n')
    print(
        pd.merge(recommendations.rename('Score'), movie_meta, left_index=True, right_index=True).to_string(index=False))


# fetch movie data
movie_meta = ml.load_movies()
movie_genres = ml.load_movie_genres()

ratings = ml.load_ratings()

# A - accept user id as input
user_id = ask_user_id(ratings.index.get_level_values(ml.user_id))

# B - display user ratings
print_user_ratings(ratings, movie_meta, user_id)

# C - recommendations
r = Recommender(movie_genres, ratings, ml.rating, ml.movie_id)
recommendations = r.recommend_movies(user_id, method=5)

print_recommendations(recommendations)
