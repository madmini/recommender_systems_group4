import functools
import os
from typing import Dict

import numpy as np
import pandas as pd
import whoosh.index as index
from django.conf import settings
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.query import Query
from whoosh.searching import Results

from util.data import Data, Column
from util.data_helper import add_poster_urls


class Search:
    index_path: str = None if not settings.configured \
        else os.path.join(settings.BASE_DIR, 'datasets', 'search_index')
    index_name: str = 'movie_index'
    ix: index.FileIndex = None

    movie_schema: Schema = Schema(
        movie_id=STORED(),
        title=TEXT(sortable=True),
        # tagline=TEXT(),
        # summary=TEXT(),
        # keywords=KEYWORD(),
        # popularity=NUMERIC(bits=64, signed=False, sortable=True),
        # genres=KEYWORD()
    )

    query_parser: QueryParser = QueryParser('title', movie_schema)

    @classmethod
    def init(cls, path: str = None, reset_index: bool = False):
        if path is None:
            path = cls.index_path

        if not os.path.exists(path):
            os.mkdir(path)

        if reset_index or not index.exists_in(path, indexname=cls.index_name):
            # create new index and fill with entries
            cls.ix = index.create_in(path, cls.movie_schema, indexname=cls.index_name)
            cls.build_index()
        else:
            # load index from disk
            cls.ix = index.open_dir(path, indexname=cls.index_name)

    @classmethod
    def build_index(cls):
        if cls.ix is None:
            cls.init()

        # automatically calls iw.commit()
        iw = cls.ix.writer()
        for movie_id, movie in Data.movie_meta().iterrows():
            # extract fields
            fields: Dict = {
                'movie_id': movie_id,
                'title': movie[Column.title.value],
                # 'tagline': movie[Column.tagline.value],
                # 'summary': movie[Column.summary.value],
                # 'keywords': movie[Column.keywords.value],
                # 'popularity': movie[Column.num_ratings.value],
                # 'genres': movie[Column.genres.value],
            }
            # filter empty values (inserting fails for np.nan values)
            fields = {
                key: val
                for key, val in fields.items()
                if val is not None and val is not np.nan and val != ''
            }

            # insert into index
            iw.update_document(**fields)

        iw.commit(optimize=True)

    @classmethod
    def _search(cls, query_text: str, n: int):
        if cls.ix is None:
            cls.init()
        if cls.ix.is_empty():
            cls.build_index()

        # ideally, the search results would internally be weighted using a TranslateFacet.
        # however this approach does not work in the current version of whoosh
        # if the search query contains multiple words

        # translation = lambda score, popularity: score**8 * popularity
        # tf = TranslateFacet(translation, ScoreFacet(), FieldFacet('popularity'))

        with cls.ix.searcher() as searcher:
            # prepare query
            query: Query = cls.query_parser.parse(query_text)
            # find better search terms based on words that appear in the content
            corrected = searcher.correct_query(query, query_text).query

            # if the corrected version of the query is different than the original, add up the search term
            if query != corrected:
                # this is done with the bitwise or operator
                # "the query results must contain the original OR the corrected terms"
                query |= corrected

            results: Results = searcher.search(query, limit=n)  # sortedby='popularity') # sortedby='tf')

            # the searcher is closed when the "with" scope is closed
            # therefore, the data needs to be extracted from the Results object
            results_dict: Dict = {movie['movie_id']: movie.score for movie in results}

            return results_dict

    @classmethod
    @functools.lru_cache(maxsize=512, typed=False)
    def search(cls, query_text: str, n: int, add_posters: bool = True):
        # this method applies a popularity bias to search results
        # as they need to be resorted, more search terms should be provided than necessary,
        # to be able to recover popular results that have rather low scores
        results = cls._search(query_text, n + 25)
        # encapsulate in pandas.Series for further operations
        scores = pd.Series(results, name='score')
        # perform a (right outer) join to connect the search results to the metadata
        df = Data.movie_meta().join(scores, how='right')
        # calculate the weighted score by raising it to some power
        # in order for the popularity to not overpower the score completely
        # and multiply with the number of ratings (the popularity)
        df.eval(f'weighted = score**16 * {Column.num_ratings.value}', inplace=True)

        # extract the n best results and export as dictionary
        d = df.nlargest(n, 'weighted').to_dict(orient='records')

        if add_posters:
            # add poster urls to the dictionary
            add_poster_urls(d)

        return d
