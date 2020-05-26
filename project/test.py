from recommendations.similar_ratings_v2 import recommend_movies

# print(recommend_movies(1, 5))
from util.data import Data

print(Data.movie_meta().loc[1])