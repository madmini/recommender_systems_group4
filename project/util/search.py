import os
from typing import Dict

import numpy as np
import whoosh.index as index
from django.conf import settings
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.query import Query
from whoosh.searching import Results

from util.data import Data, Column


class Search:
    index_path: str = None if not settings.configured \
        else os.path.join(settings.BASE_DIR, 'datasets', 'search_index')
    index_name: str = 'movie_index'
    ix: index.FileIndex = None

    movie_schema: Schema = Schema(
        movie_id=STORED(),
        title=TEXT(stored=True, field_boost=10),
        # tagline=TEXT(stored=True, field_boost=2),
        # summary=TEXT(),
        # keywords=KEYWORD(),
        # genres=KEYWORD()
    )

    qp: QueryParser = QueryParser('title', movie_schema)

    @classmethod
    def init(cls, path: str = None):
        if path is None:
            path = cls.index_path

        if not os.path.exists(path):
            os.mkdir(path)

        if index.exists_in(path, indexname=cls.index_name):
            # load index from disk
            cls.ix = index.open_dir(path, indexname=cls.index_name)
        else:
            # create new index and fill with entries
            cls.ix = index.create_in(path, cls.movie_schema, indexname=cls.index_name)
            cls.build_index()

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
                # 'genres': movie[Column.genres.value]
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

    # @classmethod
    # def reset_index(cls):
    #

    @classmethod
    def search(cls, s: str):
        if cls.ix is None:
            cls.init()

        # searcher = cls.ix.searcher()
        with cls.ix.searcher() as searcher:
            query: Query = cls.qp.parse(s)
            corrected = searcher.correct_query(query, s).query

            if query != corrected:
                query |= corrected

            print(corrected)

            r: Results = searcher.search(query)
            # if r.is_empty():
            #     r = searcher.search(corrected)

            f = [movie.fields() for movie in r]
            # searcher.close()

            return f

# if __name__ == '__main__':
#
