def compute_mean_rating(filename: str) -> float:
    try:
        with open(filename) as f:
            next(f, None)
            try:
                ratings = [float(line.split(',')[2]) for line in f]
            except (ValueError, IndexError):
                print('irregular CSV format')
                return

    except FileNotFoundError:
        print('file could not be found')
        return

    return sum(ratings) / len(ratings)


def main():
    print(compute_mean_rating('ml-latest-small/ratings.csv'))


main()
