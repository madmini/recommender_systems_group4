import numpy as np
import pandas as pd

file_path = 'the-movies-dataset/ratings_small.csv'

# the minimum amount of common movie-reviews for two users to be considered similar
min_common_movies = 3

# load ratings_small into a dataframe
df = pd.read_csv(file_path, encoding='utf8', usecols=['userId', 'movieId', 'rating'])

# group ratings by userId
df_grouped = df.groupby('userId')

# take first user as example target, try to find users similar to this one
target_user_id, target_movies = next(iter(df_grouped))

# list of similar users
similar_users = []

for current_user_id, actual_movies in df_grouped:
    # avoid comparing the user with himself
    if target_user_id == current_user_id:
        continue

    # use pd.merge (applies SQL-like join)
    # defaults to how='inner' (inner join), which is intersection
    movies_intersect = pd.merge(target_movies, actual_movies, on='movieId', suffixes=('_target', '_actual'))

    # calculate number of common movie reviews as the number of unique movieIds in the intersection
    # in case of multiple reviews per user and movie (does not seem to be the case in this dataset)
    common_movies = movies_intersect['movieId'].nunique()

    # calculate (pearson) correlation between target and current user ratings
    # only calculate if there are more than one common movie reviews
    target_ratings = movies_intersect['rating_target']
    actual_ratings = movies_intersect['rating_actual']
    correlation = target_ratings.corr(actual_ratings) if common_movies > 1 else np.nan

    if common_movies >= min_common_movies:
        # add user to dictionary
        similar_users += [{
            'userId': current_user_id,
            'commonMovies': common_movies,
            'correlation': correlation,
            'similarity': common_movies * correlation,
        }]
        # print("user {0} is considered similar with {1} common movies and correlation {2}"
        #      .format(current_user_id, common_movies, correlation))

df_similar_users = pd.DataFrame(similar_users)

print(df_similar_users)

print(df_similar_users.nlargest(5, ['commonMovies'], keep='all'))

print(df_similar_users.nlargest(5, ['correlation'], keep='all'))

print(df_similar_users.nlargest(5, ['similarity'], keep='all'))
