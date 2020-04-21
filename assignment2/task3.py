import numpy as np
import pandas as pd
from typing import Optional


# preprocess the csv in order for it to be read correctly
# detects newlines within quotes, replaces them with "\n"
# (pandas.read_csv does not detect quoted newlines)
def pre_process(source_path: str, target_path: str, num_cols: Optional[int]) -> None:
    # read from source file
    with open(source_path, encoding='utf8') as source:
        # overwrite target file
        with open(target_path, 'w', encoding='utf8', newline='\n') as target:

            for line in source:
                column_count, has_unclosed_quotes = count_columns(line)

                # if the expected number of columns is not specified, infer from first line
                if num_cols is None:
                    num_cols = column_count

                # if unproperly formatted lines are encountered, try to append the next line and check again
                # stop if the number of columns is higher than expected
                while has_unclosed_quotes or column_count < num_cols:
                    # remove the newline from the first line, replace with explicit "\n"
                    line = line.rstrip() + '\\n' + next(source)
                    column_count, has_unclosed_quotes = count_columns(line)

                # if the line had no errors, or they were fixed, output the line
                # this will be skipped if the number of columns exceeds the expected number,
                # and the while loop ended before a closing quote could be found
                if not has_unclosed_quotes:
                    target.write(line)


# return the number of csv columns and a bool indicating whether any quotes are left unclosed
# is able to detect quoted sections
# returns (number of colums, has_unclosed_quotes)
def count_columns(line: str) -> (int, bool):
    # if the current symbol is within a quoted section
    active_quote = False
    # the previous symbol
    prev = None
    column_count = 1

    for char in line:
        # if unescaped quote is encountered
        if char == '"' and prev != '\\':
            # toggle quote
            active_quote = not active_quote
        # else, if a comma outside of quotes is encountered
        elif char == ',' and not active_quote:
            # increment column count
            column_count += 1

        prev = char

    return column_count, active_quote


raw_path = 'the-movies-dataset/movies_metadata.csv'
processed_path = 'the-movies-dataset/movies_metadata.prep.csv'

# apply pre-processing (replace quoted newlines, as read_csv does not detect or fix them)
pre_process(raw_path, processed_path, 24)

# read dataframe from csv, column names are inferred automatically
# specify parsing dates for the 'release_date' column as dates will be used for comparison later
df = pd.read_csv(processed_path, encoding='utf8', parse_dates=['release_date'], infer_datetime_format=True)

print(type(df))
# <class 'pandas.core.frame.DataFrame'>

# print first and last movie, access using iloc (integer-location)
# request the first (0) and the last (-1) entry (request using list [1, -1] in one call)
print(df.iloc[[0, -1]].to_string())

# print info about 'Jumanji'. use pandas query syntax
# df['title'] returns a one-dimensional list of titles (just the title column)
# df['title'] == 'Jumanji' returns a bitmap showing which rows have a title equal to 'Jumanji'
# df[df['title'] == 'Jumanji'] applies the bitmap to the full dataframe returning only the matching rows
print(df[df['title'] == 'Jumanji'].to_string())

# reduce set of columns
# same idea, specify list of columns to return
small_df = df[['title', 'release_date', 'popularity', 'revenue', 'runtime', 'genres']]

# filter for release dates greater (later) than 2010-01-01
# this requires enabling date parsing by specifying parse_dates=['release_date'] on read_csv
print(small_df[small_df['release_date'] > np.datetime64('2010-01-01')])
