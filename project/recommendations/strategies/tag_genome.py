import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from util.data import Data


class TagGenome:
    similarity_matrix: np.ndarray

    @classmethod
    def tag_similarity(cls):
        t = Data.tag_genome()
        cls.similarity_matrix = cosine_similarity(t)
        return cls.similarity_matrix

    def __call__(self, movie_id: int, n: int = 5):
        tg = Data.tag_genome()
        index = tg.index.get_loc(movie_id)
        similarities = self.tag_similarity()[index]
        sr = pd.Series(index=tg.index, data=similarities)
        return sr.drop(movie_id)
