import recommendations.strategies.cast_and_crew
from recommendations.strategies import tf_idf, cast_and_crew
from recommendations.strategies.shared import relevance_helper
from util.data import Column

def recommend_movies(movie_id: int, n: int = 5,keywords_ml_importance:float=1.0,genre_importance:float=0.8, actors_importance:float=0.1,directors_importance=0.1, year_importance=0.05):
    calculations_df= recommendations.strategies.cast_and_crew.same_directors(movie_id, n).to_frame()
    calculations_df['actors']= cast_and_crew.same_actors(movie_id, n).values
    calculations_df['keywords']= tf_idf.TfIdfSimilarity.get_similarities_for(movie_id, 'tmdb_keywords')
    calculations_df['genres']= relevance_helper.get_genre_overlap_values(movie_id)
    calculations_df['year_difference']= relevance_helper.get_year_relevance(movie_id)

    calculations_df['result']=  calculations_df['directors']*directors_importance    \
                                + calculations_df['actors']*actors_importance        \
                                + calculations_df['keywords']*keywords_ml_importance \
                                + calculations_df['genres'] * genre_importance       \
                                + calculations_df['year_difference'] * year_importance
    return calculations_df['result']
