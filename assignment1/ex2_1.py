with open('ml-latest-small/ratings.csv') as f:
    # skip headers (set default=None in case f is empty as next would raise StopIteration)
    next(f, None)
    ratings = [float(line.split(',')[2]) for line in f]

print(sum(ratings) / len(ratings))
