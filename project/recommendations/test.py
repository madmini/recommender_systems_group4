from typing import List, Dict
import pandas as pd
from util.data import Data, Column

def recommend_movies(movie_id: int, n: int) -> List[int]:
    ratings = Data.ratings()
    ratings = ratings.reset_index()
    ratedUsers = ratings.loc[ratings['movie_id'] == movie_id][['user_id']]
    ratedUsersRating = ratedUsers.merge(ratings, left_on='user_id', right_on='user_id')
    ratedUsersRating = ratedUsersRating.drop(ratedUsersRating[ratedUsersRating['movie_id'] == movie_id].index)

    countedSumRatings = ratedUsersRating.groupby('movie_id').agg({'rating': 'sum', 'user_id': 'count'}).reset_index()
    countedSumRatings[['rating']] = countedSumRatings[['rating']].div(countedSumRatings['user_id'].values, axis=0)

    resultRatings = countedSumRatings.sort_values(by=['rating'], ascending=False)
    resultRatings = resultRatings.head(n)
    resultRatings = resultRatings['movie_id'].values.tolist()

    return resultRatings
