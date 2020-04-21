The solutions for the tasks of Assignment 2 are contained in files as follows.

task    scripts         assets (in the-movie-dataset/)
----    ----------      -------------------------------------------
2.1     task2_1.py
2.2     task2_2.py
3       task3.py        movie_metadata.csv, movie_metadata.prep.csv
4       task4.py        ratings_small.csv
5       task5.py        ratings_small.csv


Notes for tasks:

    3   As movies_metadata.csv contains quoted newlines that neither pandas nor csv (the package) are able to read
        a step of pre-processing was added. Quoted newlines are replaced with "\n". In this step,
        movies_metadata.csv is not overwritten. Instead, the new file movies_metadata.prep.csv is created.

        In order to compare the release year of movies, the parameter parse_dates=['release_date'] is passed
        to pandas.read_csv. This enables filtering the DataFrame by direct comparison.

    4   Instead of iterating over the groups, .aggregate() was used with NamedAgg.

    5   Instead of extracting sets of rated movies for each users, intersections are created directly via pandas.merge.
