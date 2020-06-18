import functools
from typing import Dict

import requests
from django.conf import settings

api_keys_filename = 'apikeys.secret.json'

api_key_names = {
    'omdb': 'OMDB_API_KEY',
    'tmdb_v3': 'TMDB_API_V3_KEY',
    'tmdb_v4': 'TMDB_API_V4_KEY',
}


class Poster:
    _poster_size: str = 'w342'
    _api_keys: Dict[str, str] = dict()
    _tmdb_api_conf = {
        "images": {
            "base_url": "http://image.tmdb.org/t/p/", "secure_base_url": "https://image.tmdb.org/t/p/",
            "backdrop_sizes": ["w300", "w780", "w1280", "original"],
            "poster_sizes": ["w92", "w154", "w185", "w342", "w500", "w780", "original"],
        },
    }

    @classmethod
    def init(cls, api_key_file_path: str = None, update_tmdb_config: bool = False):
        import os
        import simplejson

        if api_key_file_path is None:
            api_key_file_path = os.path.join(settings.BASE_DIR, 'util', api_keys_filename)

        if os.path.exists(api_key_file_path):
            j: Dict
            with open(api_key_file_path, encoding='utf8') as f:
                j = simplejson.load(f, encoding='utf8')

            for api_key in api_key_names:
                if api_key_names[api_key] in j:
                    cls._api_keys[api_key] = j[api_key_names[api_key]]

        if update_tmdb_config:
            r = requests.get(
                'https://api.themoviedb.org/3/configuration',
                params={'apikey': cls._api_keys[api_key_names['tmdb_v3']]}
            )

            j = r.json()

            if not r.ok or 'success' in j and j['success'] == 'false':
                raise Exception(j['status_message'], j)

            cls._tmdb_api_conf = j

    @classmethod
    def set_poster_size(cls, poster_size: int):
        sizes = cls._tmdb_api_conf['images']['poster_sizes']

        try:
            cls._poster_size = next(size for size in sizes if cls.get_poster_size(size) >= poster_size)

        except StopIteration:
            cls._poster_size = 'original'

    @staticmethod
    def get_poster_size(s: str) -> int:
        try:
            return int(s.lstrip('w'))
        except ValueError:
            return 0

    @classmethod
    def _get_api_key(cls, name: str):
        if name not in cls._api_keys:
            cls.init()
        if name not in cls._api_keys:
            return None

        return cls._api_keys[name]

    @classmethod
    @functools.lru_cache(maxsize=None, typed=False)
    def get_poster_tmdb(cls, tmdb_movie_id: int, poster_size: str = None) -> str:
        if poster_size is None:
            poster_size = cls._poster_size

        api_key = cls._get_api_key('tmdb_v3')
        if api_key is None:
            return ''

        r = requests.get(
            'https://api.themoviedb.org/3/movie/%s/images' % tmdb_movie_id,
            params={
                'api_key': api_key,
                # 'include_image_language': 'en,null'
            },
        )

        j = r.json()

        if not r.ok or 'success' in j and j['success'] == 'false':
            return ''
            # raise Exception(j['status_message'], j)

        if len(j['posters']) == 0:
            return ''

        # prefer posters in known language: english > german > no assigned language (no text on poster)
        poster = None
        for lang in ['en', 'de', None]:
            try:
                poster = next(poster for poster in j['posters'] if poster['iso_639_1'] == lang)
                break
            except StopIteration:
                pass

        # if none of preferred languages are available, just pick first poster
        if poster is None:
            poster = j['posters'][0]

        # assemble poster url from parts
        poster_url = str(cls._tmdb_api_conf['images']['base_url']) + str(poster_size) + str(poster['file_path'])

        return poster_url

    @classmethod
    def get_poster_tmdb_ml(cls, movielens_id: int) -> str:
        from util.data import Data, Column

        tmdb_movie_id = Data.movie_meta().at[movielens_id, Column.tmdb_id.value]
        return cls.get_poster_tmdb(tmdb_movie_id=tmdb_movie_id)

    @classmethod
    def request_tmdb_api_v4(cls):
        api_key = cls._get_api_key('tmdb_v4')
        if api_key is None:
            return ''

        r = requests.get(
            'https://api.themoviedb.org/4/list/1',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json;charset=utf-8'
            }
        )

        j = r.json()

        if not r.ok or 'success' in j and j['success'] == 'false':
            return ''

    @classmethod
    def get_poster_omdb_imdb(cls, imdb_movie_id: str = None) -> str:
        api_key = cls._get_api_key('omdb')
        if api_key is None:
            return ''

        r = requests.get(
            'http://www.omdbapi.com/',
            params={
                'i': imdb_movie_id if imdb_movie_id.startswith('tt') else 'tt' + imdb_movie_id,
                'apikey': api_key
            }
        )

        j = r.json()

        if not r.ok or 'Response' in j and j['Response'] == 'False':
            return ''
        else:
            return r.json()['Poster']

    @classmethod
    def get_poster_omdb_ml(cls, movielens_id: int) -> str:
        from util.data import Data, Column

        imdb_movie_id = Data.movie_meta().at[movielens_id, Column.imdb_id.value]
        return cls.get_poster_omdb_imdb(imdb_movie_id=imdb_movie_id)
