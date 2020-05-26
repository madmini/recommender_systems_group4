import requests

from util.data import Data

OMDB_API_KEY = '93d58438'


def get_poster_omdb_imdb(imdb_movie_id: str = None) -> str:
    r = requests.get('http://www.omdbapi.com/', {
        'i': imdb_movie_id if imdb_movie_id.startswith('tt') else 'tt' + imdb_movie_id,
        'apikey': OMDB_API_KEY
    })

    j = r.json()

    if j['Response'] == 'False':
        return ''
    else:
        return r.json()['Poster']


def get_poster_omdb_ml(movielens_id: int) -> str:
    imdb_movie_id = Data.movie_meta().at[movielens_id, 'imdbMovieId']
    return get_poster_omdb_imdb(imdb_movie_id=imdb_movie_id)
