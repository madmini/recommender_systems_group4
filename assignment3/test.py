import functools
import pandas as pd
import time


# timer wrapper function, used to find runtime of functions in testing
def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        tic = time.perf_counter()
        value = func(*args, **kwargs)
        toc = time.perf_counter()
        elapsed_time = toc - tic
        print(f"Elapsed time: {elapsed_time:0.4f} seconds")
        return value

    return wrapper_timer


ratings_header = ['UserID', 'MovieID', 'Rating', 'Timestamp']

ratings_path: str = 'ml-1m/ratings.dat'
ratings_prep_path: str = 'ml-1m/ratings.prep.dat'


# load with python engine
@timer
def load(file_name: str) -> pd.DataFrame:
    return pd.read_csv(ratings_path, sep='::', names=ratings_header, engine='python')


# pre-processing step, replace '::' with ','
# @timer
def prep(file_name: str, prep_file_name: str) -> None:
    with open(file_name) as source, open(prep_file_name, 'w') as target:
        for line in source:
            target.write(line.replace('::', ','))


# load with pre-processing
@timer
def load_with_prep(file_name: str, prep_file_name: str) -> pd.DataFrame:
    prep(file_name, prep_file_name)

    return pd.read_csv(prep_file_name, names=ratings_header)  # , engine='c')


@timer
def load_mem(file_name: str) -> pd.DataFrame:
    with open(file_name) as file:
        data = file.read()

    return pd.read_csv(data.replace('::', ','), names=ratings_header, engine='c')


@timer
def load_alt(file_name: str) -> pd.DataFrame:
    return pd.read_table(file_name, sep=':', usecols=[0, 2, 4, 6], names=ratings_header, engine='c')


load(ratings_path)

load_with_prep(ratings_path, ratings_prep_path)

# load_mem(ratings_path)

load_alt(ratings_path)

# print(df)
