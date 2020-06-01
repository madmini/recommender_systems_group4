from typing import List
import pandas as pd

from util.data import Data
from util.data_helper import get_movie_meta_for

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# should be in a method like the __init__ (need to look into this)
tfidf = TfidfVectorizer(stop_words='english')
needed_columns=['tmdb_keywords','genres','tmdb_title','tmdb_tagline','actors','tmdb_popularity','tmdb_vote_count','tmdb_vote_average','imdb_writers','directors','release_year']

meta= Data.movie_meta()
# need to do this so i can get a index column to identify the output from the ML-Algorithm (only gives me the ROW-NUMBER)
movie_data=meta[needed_columns].copy()
movie_data.reset_index(inplace=True)
movie_data.fillna({'tmdb_popularity':0,'tmdb_vote_count':0,'tmdb_vote_average':0,'release_year':0},inplace=True)
movie_data.fillna('',inplace=True)

tfidf_matrix = tfidf.fit_transform(movie_data['tmdb_keywords'])
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

def recommend_movies(movie_id: int, n: int) -> List[int]:
    index= movie_data[movie_data['movie_id']==movie_id].index.tolist()[0]
    sim_scores = list(enumerate(cosine_sim[index]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[0:n+1]
    recommended_movie_ids = [movie_data['movie_id'].iloc[i[0]] for i in sim_scores]
    recommended_movie_ids.remove(movie_id)
    print(recommended_movie_ids)
    return recommended_movie_ids