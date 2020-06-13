from typing import Dict

import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from util.data import Data, Column


class TfIdfSimilarity:
    tf_idf = TfidfVectorizer(stop_words='english')
    similarity_matrices: Dict[str, csr_matrix] = dict()

    @classmethod
    def calculate_similarities(cls, colname: str, overwrite_existing: bool = False):
        if colname not in cls.similarity_matrices or overwrite_existing:
            # calculate tf_idf for column
            tfidf_matrix = cls.tf_idf.fit_transform(Data.movie_meta()[colname].fillna(''))
            # calculate similarities between movies
            # use dense_output=False (results in sparse matrix) to reduce memory usage
            cls.similarity_matrices[colname] = linear_kernel(tfidf_matrix, tfidf_matrix, dense_output=False)

        return cls.similarity_matrices[colname]

    @classmethod
    def get_similarities_for(cls, movie_id: int, colname: str):
        # get similarity matrix (calculate if necessary)
        sim_matrix = cls.calculate_similarities(colname)

        # get absolute index of movie
        index = Data.movie_meta().index.get_loc(movie_id)

        # get similarities for this movie
        # use .toarray() to convert from sparse matrix
        # use [0] to convert "matrix" with only one row to one-dimensional array
        similarities = sim_matrix[index].toarray()[0]

        # put into pandas Series
        # use index=... to apply original index
        series = pd.Series(index=Data.movie_meta().index, data=similarities)

        return series.drop(movie_id)

    @classmethod
    def recommend(cls, movie_id: int, n: int = 5) -> pd.Series:
        return cls.get_similarities_for(movie_id, Column.keywords.value)
