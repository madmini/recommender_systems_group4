This application is designed to work on any MovieLens-like dataset.
The datafiles can be accessed through the data.py library.

datasets:

  full_meta    full metadata (movielens+imdb+tmdb) provided with assignment
  ml-*         movielens datasets


notes:

    full_meta

        this dataset was provided as a set of ~45k json files.
        those have been combined into movie_meta_full.csv or movie_meta.csv by running preprocessing/json_to_csv.py
        movie_meta.csv contains a version stripped of redundant/unnecessary information.

    ml-*

        Any such dataset must be a direct sub-directory named ml-<name> (where <name> can be any string),
        and must contain the following datafiles: ratings, movies, and links.
        The datafiles must be formatted as CSV (',' separated) or DAT ('::' separated),
        and may be compressed in one of the pandas-supported formats (e.g. using 7-zip):
            <name>.<ext>.xz  (strongest compression)
            <name>.<ext>.bz2 (bzip2)
            <name>.<ext>.zip (normal .zip)
            <name>.<ext>.gz  (gzip)
            <name>.<ext>     (no compression)
        for more info on supported compression see https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
