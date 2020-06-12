"""
adapter for the datasets of this project

provides a load functions
"""
import os
from enum import Enum
from typing import List, Dict

import pandas as pd

from util.synchronized import synchronized

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataset_dir = os.path.join(BASE_DIR, 'datasets')
meta_dataset_dir = os.path.join(dataset_dir, 'full_meta')


class Column(Enum):
    user_id = 'user_id'
    movie_id = 'movie_id'
    rating = 'rating'
    timestamp = 'timestamp'
    title = 'title'
    genres = 'genres'
    gender = 'gender'
    age = 'age'
    occupation = 'occupation'
    zip_code = 'zip_code'
    imdb_id = 'imdb_id'
    tmdb_id = 'tmdb_id'
    tag = 'tag'
    actors = 'actors'
    directors = 'directors'
    release_year = 'release_year'
    release_date = 'release_date'
    summary = 'summary'
    tagline = 'tmdb_tagline'
    keywords = 'tmdb_keywords'
    poster_url = 'poster'
    num_ratings = 'numRatings'
    tmdb_similar = 'tmdb_recommendations'
    collection = 'tmdb_belongs_to_collection'

    def __str__(self):
        return self.value


class File(Enum):
    # ratings.dat - UserID::MovieID::Rating::Timestamp
    ratings = (
        'ratings',
        [Column.user_id.value, Column.movie_id.value, Column.rating.value, Column.timestamp.value],
        [Column.user_id.value, Column.movie_id.value],
        {Column.rating.value: 'float64', Column.timestamp.value: 'int32'},
    )
    # movies.dat - MovieID::Title::Genres
    movies = ('movies', [Column.movie_id.value, Column.title.value, Column.genres.value], Column.movie_id.value)
    # users.dat - UserID::Gender::Age::Occupation::Zip-code
    users = (
        'users',
        [Column.user_id.value, Column.gender.value, Column.age.value, Column.occupation.value, Column.zip_code.value],
        Column.user_id.value
    )
    # tags.csv: userId, movieId, tag, timestamp
    tags = ('tags', [Column.user_id.value, Column.movie_id.value, Column.tag.value, Column.timestamp.value], None)
    # links.csv: movieId,imdbId,tmdbId
    links = ('links', [Column.movie_id.value, Column.imdb_id.value, Column.tmdb_id.value], None)
    movie_meta = (
        'movie_meta',
        [Column.movie_id.value, 'tmdb_original_language', Column.keywords.value, 'tmdb_video',
         'tmdb_title', Column.tmdb_similar.value, 'tmdb_backdrop_path', 'tmdb_revenue', 'tmdb_genres',
         'tmdb_popularity', 'tmdb_production_countries', 'tmdb_vote_count', 'tmdb_budget', 'tmdb_similar',
         'tmdb_original_title', 'tmdb_spoken_languages', 'tmdb_production_companies', 'tmdb_vote_average',
         Column.collection.value, Column.tagline.value, 'tmdb_adult', 'tmdb_homepage', 'tmdb_status', 'imdb_country',
         'imdb_color', 'imdb_budgetCurrency', 'imdb_directors', 'imdb_runtime', 'imdb_writers', 'imdb_originalLanguage',
         'imdb_coverLink', 'imdb_genres', 'imdb_productionCompanies', 'imdb_budget', 'languages',
         Column.release_date.value, 'dvdReleaseDate', Column.directors.value, 'runtime', 'movielens_id',
         Column.title.value, 'mpaa', Column.actors.value, Column.imdb_id.value, 'originalTitle', Column.genres.value,
         'youtubeTrailerIds', Column.summary.value, Column.tmdb_id.value, 'avgRating', Column.release_year.value,
         Column.num_ratings.value, 'posterPath'],
        0,
        {'tmdb_adult': 'boolean', 'tmdb_video': 'boolean',
         'tmdb_budget': 'Int64', 'tmdb_revenue': 'Int64',
         'tmdb_vote_count': 'Int16', Column.imdb_id.value: 'str', Column.release_year.value: 'Int16',
         'runtime': 'Int16', 'tmdb_status': 'category', 'mpaa': 'category',
         'imdb_originalLanguage': 'category', 'imdb_color': 'category', 'imdb_country': 'category',
         Column.collection.value: 'category'}
    )

    def __init__(self, filename: str, header: List[str], index: List[str], dtypes: Dict[str, str] = None):
        self.filename = filename
        self.header = header
        self.index = index
        self.dtypes = dtypes

    def __str__(self):
        return self.filename


class Data:
    __ml_path: str = None

    __file_paths: Dict[File, str] = None
    __cache: Dict[File, pd.DataFrame] = None

    @classmethod
    @synchronized
    def init(cls, ml_path: str = None, preload_files: bool = False):

        max_size = 0

        if ml_path is not None:
            if os.path.exists(ml_path):
                cls.__ml_path = ml_path
            else:
                p = os.path.join(dataset_dir, ml_path)
                if os.path.exists(p):
                    cls.__ml_path = p
                else:
                    p = os.path.join(BASE_DIR, ml_path)
                    if os.path.exists(p):
                        cls.__ml_path = p

        cls.__file_paths = dict()
        cls.__cache = dict()

        if cls.__ml_path is None:
            files: Dict[str, str] = None

            for name in os.listdir(dataset_dir):
                if not name.startswith('ml-'):
                    continue

                current_ml_path: str = os.path.join(dataset_dir, name)

                current_files: Dict[str, str] = {file.split('.')[0]: file for file in os.listdir(current_ml_path)}

                if File.ratings.filename not in current_files or File.movies.filename not in current_files:
                    continue

                ratings_size: int = os.path.getsize(os.path.join(current_ml_path, current_files[File.ratings.filename]))
                if ratings_size > max_size:
                    cls.__ml_path = current_ml_path
                    max_size = ratings_size
                    files = current_files

        else:
            files = {file.split('.')[0]: file for file in os.listdir(cls.__ml_path)}

        if cls.__ml_path is None or files is None:
            print('no movielens "ml-*" dataset found')
        else:
            lookup_files = {file.filename: file for file in File}

            for name in files:

                full_name = files[name]

                if name in lookup_files:
                    file = lookup_files[name]
                    cls.__file_paths[file] = os.path.join(cls.__ml_path, full_name)

        # print("using " + str(cls.__ml_path))

        for name in os.listdir(meta_dataset_dir):
            if name.startswith('movie_meta.csv'):
                cls.__file_paths[File.movie_meta] = os.path.join(meta_dataset_dir, name)
                if not name.endswith(('.xz', '.gz', '.zip', '.bz2')):
                    break

        if preload_files:
            cls.movies()
            cls.ratings()
            cls.movie_meta()

    @classmethod
    def movie_genre_dummies(cls) -> pd.DataFrame:
        # split the genre column into "boolean" columns: (put into separate dataframe for now)
        #   each genre becomes a new column, with a value of 1 if the movie has the respective genre, and 0 if not
        return cls.movies().pop(Column.genres.name).str.get_dummies(sep='|')

    @classmethod
    @synchronized
    def movies(cls) -> pd.DataFrame:

        if cls.__file_paths is None:
            cls.init()

        file = File.movies

        if file not in cls.__file_paths:
            return None

        path = cls.__file_paths[file]

        if file not in cls.__cache:

            if '.dat' in path:
                # using ansi (Windows CP-1252) encoding
                # use index to avoid duplicate/unnecessary indexing, as the datafiles already have primary keys
                cls.__cache[file] = pd.read_csv(
                    path, sep='::', engine='python', encoding='ansi', dtype=file.dtypes, names=file.header, header=0)
            else:
                cls.__cache[file] = pd.read_csv(path, dtype=file.dtypes, names=file.header, header=0)

            cls.__cache[file].set_index(file.index)

        return cls.__cache[file]

    @classmethod
    @synchronized
    def ratings(cls, include_timestamps: bool = False, use_multi_index: bool = False) -> pd.DataFrame:

        if cls.__file_paths is None:
            cls.init()

        file = File.ratings

        header = file.header
        if not include_timestamps:
            header = header[:-1]

        if file not in cls.__file_paths:
            return None

        if file not in cls.__cache:
            path = cls.__file_paths[file]

            if '.dat' in path:
                # this method is faster than the more obvious alternatives
                #   assign single ':' as the separator, then ignore odd columns with usecols=<even numbers>
                #   this utilizes the c based scanning engine which faster by an order of magnitude
                #   this is not applicable for the movies file, as its title column contains colons
                # using ansi (Windows CP-1252) encoding
                usecols = range(0, 2 * len(header), 2)
                cls.__cache[file] = pd.read_csv(
                    path, sep=':', encoding='ansi', usecols=usecols, dtype=file.dtypes, names=header, header=0)
            else:
                usecols = range(0, len(header))
                cls.__cache[file] = pd.read_csv(path, usecols=usecols, dtype=file.dtypes, names=header, header=0)

            # use index to avoid duplicate/unnecessary indexing, as the datafiles already have primary keys
            # Note: read_csv has an option for this, however apparently uses unstable APIs when generating a multi-index
            cls.__cache[file].set_index(keys=file.index, inplace=True)

        if use_multi_index:
            return cls.__cache[file]
        else:
            return cls.__cache[file].reset_index()

    @classmethod
    def ratings_as_series(cls) -> pd.Series:
        # since there is only one real column, squeeze the columns into a single series
        return cls.ratings(include_timestamps=False, use_multi_index=True).squeeze(axis='columns')

    @classmethod
    @synchronized
    def movie_meta(cls) -> pd.DataFrame:

        if cls.__file_paths is None:
            cls.init()

        file = File.movie_meta

        if file not in cls.__file_paths:
            return None

        path = cls.__file_paths[file]

        if file not in cls.__cache:
            cls.__cache[file] = pd.read_csv(
                path, index_col=0, engine='c', names=file.header, header=0,
                dtype=file.dtypes, parse_dates=[Column.release_date.value]
            )
            # cls.__cache[file].rename_axis('movieId', inplace=True)

        return cls.__cache[file]

    @classmethod
    def load(cls, f: File):
        if f == File.ratings:
            cls.ratings()
        elif f == File.movies:
            cls.movies()
        elif f == File.movie_meta:
            cls.movie_meta()
