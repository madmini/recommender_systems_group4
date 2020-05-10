This application is designed to work on any MovieLens-like dataset.
The datafiles can be accessed through the data.py library.

datasets:

  ml-*         movielens datasets
  full_meta    full metadata (movielens+imdb+tmdb) provided with assignment



notes:

    full_meta

        this dataset was provided as a set of ~45k json files. those have been combined into movie_meta_full.csv.
        movie_meta.csv contains a version stripped of redundant/unnecessary information.

    ml-*

        Any such dataset must be a direct sub-directory named ml-<name> (where <name> can be any string),
        and must contain the following datafiles: ratings, movies, and links.
        The datafiles must be formatted as CSV,
        and may be compressed in one of the pandas-supported formats (e.g. using 7-zip):
            <name>.csv.xz  (strongest compression)
            <name>.csv.bz2 (bzip2)
            <name>.csv.zip (normal .zip)
            <name>.csv.gz  (gzip)
            <name>.csv     (no compression)
        for more info on supported compression see https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
