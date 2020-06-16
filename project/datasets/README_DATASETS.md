# Datasets

This application is designed to work on any MovieLens-like dataset.  
The datafiles can be accessed through the data.py library.

## Datasets used by the implementation

### `full_meta/` 
Full metadata (movielens+imdb+tmdb). This dataset was provided with the assignment as a set of ~45k `.json` files.

These files have been combined into a single CSV file
by running [our preprocessing script]( ../preprocessing/json_to_csv.py ).  
`movie_meta.csv` contains a version stripped of what we deem redundant/unnecessary information
in regards to our recommendation strategies; 
the full version is compiled as `movie_meta_full.csv`.

### `ml-*/`
Movielens datasets. `ml-latest-small` is included per default.

Any such dataset must be a direct sub-directory named `ml-<name>` (where `<name>` can be any string),
and must contain at least a `ratings` datafile.
The datafiles must be formatted as CSV (`,`-separated) or DAT (`::`-separated),
and may be compressed in one of the pandas-supported formats (e.g. using 7-zip):
- `<name>.<ext>.xz`  (strongest available compression)
- `<name>.<ext>.bz2` (bzip2)
- `<name>.<ext>.zip` (normal .zip)
- `<name>.<ext>.gz`  (gzip)
- `<name>.<ext>`     (no compression)

_For more info on supported compression see the 
[pandas documentation]( https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html )_.
