import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from util.data import Data

# should be in a method like the __init__ (need to look into this)
tf_idf = TfidfVectorizer(stop_words='english')
needed_columns = ['tmdb_keywords', 'genres', 'tmdb_title', 'tmdb_tagline', 'actors', 'tmdb_popularity',
                  'tmdb_vote_count', 'tmdb_vote_average', 'imdb_writers', 'directors', 'release_year']

meta = Data.movie_meta()
# need to do this so i can get a index column to identify the output from the ML-Algorithm
# (only gives me the ROW-NUMBER)
movie_data = meta[needed_columns].copy()
# movie_data.reset_index(inplace=True)
movie_data.fillna({'tmdb_popularity': 0, 'tmdb_vote_count': 0, 'tmdb_vote_average': 0, 'release_year': 0}, inplace=True)
movie_data.fillna('', inplace=True)

tf_idf_matrix = tf_idf.fit_transform(movie_data['tmdb_keywords'])
cosine_sim: csr_matrix = linear_kernel(tf_idf_matrix, tf_idf_matrix, dense_output=False)


def recommend_movies(movie_id: int, n: int = 5) -> pd.Series:
    index = Data.movie_meta().index.get_loc(movie_id)

    similarities = cosine_sim[index].toarray()[0]

    series = pd.Series(index=Data.movie_meta().index, data=similarities)

    return series.drop(movie_id)
