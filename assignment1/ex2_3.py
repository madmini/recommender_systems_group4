# more complicated than necessary,
# but is able to output multiple modes (if more than one rating has the max amount of views)
# and does not rely on sorting the whole list of ratings
def compute_mean_rating(filename: str) -> (float, float, {float}):
    # dictionary of: rating => number of reviews that contained this rating
    ratings = dict()
    # number of reviews
    count = 0
    total = 0

    try:
        with open(filename) as f:
            next(f, None)
            for line in f:
                try:
                    rating_str = line.split(',')[2]
                except IndexError:
                    continue

                rating = float(rating_str)
                ratings[rating] = ratings[rating] + 1 if rating in ratings else 1
                count += 1
                total += rating

    except FileNotFoundError:
        print('file could not be found')
        return

    count2 = 0
    prev = None
    max_count = 0
    modes = {}
    median = None

    # iterate over the dictionary
    # note that this does not sort the whole list of ratings, just the set of different ratings
    for r in sorted(ratings):
        num_ratings = ratings[r]

        # find and add modes
        if num_ratings > max_count:
            # new max number of reviews, replace old mode(s)
            max_count = num_ratings
            modes = {r}
        elif num_ratings == max_count:
            # same amount of reviews, add to set
            modes += r

        # check if position for median is reached
        count2 += num_ratings
        if median is None and count2 >= (count // 2):
            if count % 2 == 1:
                median = r
            else:
                if count2 - num_ratings >= count // 2 - 1:
                    median = (r + prev) / 2
                else:
                    median = r
        prev = r

    return total / count, median if median is not None else -1, modes


def main():
    print(compute_mean_rating('ml-latest-small/ratings.csv'))


main()
