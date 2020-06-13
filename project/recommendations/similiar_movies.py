import pandas as pd

from util.data import Data
from recommendations import  similarity_ml, same_actors, same_directors
from recommendations.shared import relevance_helper

def recommend_movies(movie_id: int, n: int= None,keywords_ml_importance:float=1.0,genre_importance:float=0.8, actors_importance:float=0.1,directors_importance=0.1, year_importance=0.05):
    calculations_df=same_directors.recommend_movies(movie_id,n).to_frame()
    calculations_df['actors']=same_actors.recommend_movies(movie_id,n).values
    calculations_df['keywords']=similarity_ml.recommend_movies(movie_id,n)
    calculations_df['genres']=relevance_helper.get_genre_overlap_values(movie_id)
    calculations_df['year_difference']= relevance_helper.get_year_relevance(movie_id)

    calculations_df['result']=  calculations_df['directors']*directors_importance    \
                                + calculations_df['actors']*actors_importance        \
                                + calculations_df['keywords']*keywords_ml_importance \
                                + calculations_df['genres'] * genre_importance       \
                                + calculations_df['year_difference'] * year_importance
    return calculations_df['result']
