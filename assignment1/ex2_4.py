import csv
from typing import Dict


def show_genres(filename: str) -> Dict[str, int]:
    # newline='' is recommended for use with the csv package
    # encoding='utf8' necessary for movies.csv, as titles use special chars
    with open(filename, newline='', encoding='utf8') as f:
        # dict genre -> number of movies with this genre
        genre_dict = dict()

        # skip headers
        next(f, None)

        for row in csv.reader(f):
            # iterate through genres for movie
            for genre in str(row[2]).split('|'):
                # increment count in genre_dict, or add genre with count 1 if not present
                genre_dict[genre] = genre_dict[genre] + 1 if genre in genre_dict else 1

    # sort genres by count, descending (select key as item[1] being the count)
    sorted_genres = sorted(genre_dict.items(), key=lambda item: item[1], reverse=True)

    # return in new sorted dict
    return {genre: count for genre, count in sorted_genres}


def main():
    print(show_genres('ml-latest-small/movies.csv'))


main()
