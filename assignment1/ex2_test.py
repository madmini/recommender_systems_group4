import statistics

import ex2_3
import ex2_5

ratings_path = 'ml-latest-small/ratings.csv'
movies_path = 'ml-latest-small/movies.csv'

with open(ratings_path) as f:
    next(f, None)
    ratings = [float(line.split(',')[2]) for line in f]

mean = statistics.mean(ratings)
median = statistics.median(ratings)
mode = statistics.mode(ratings)

ex2_3_result = ex2_3.compute_mean_rating(ratings_path)
if ex2_3_result == (mean, median, {mode}):
    print('test 2.3 pass')
else:
    print('test 2.3 fail')

ex2_5_result = ex2_5.Statistics.compute_mean_rating(ratings_path)
if ex2_5_result == mean:
    print('test 2.5 pass')
else:
    print('test 2.5 fail')
