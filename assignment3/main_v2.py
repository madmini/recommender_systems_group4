import pandas as pd

# HEADERS
movieHeader = ['MovieId', 'Title', 'Genre']
ratingsHeader = ['UserId', 'MovieId', 'Ratings', 'Timestamp']
userHeader = ['UserId', 'Gender', 'Age', 'Occupation', 'ZipCode']  #
neighbors_header = ['UserId', 'Distance']
# Import the 3 Files with named columns (from the README)
movieData = pd.read_csv('ml-1m/movies.dat', sep='::', engine='python', header=None, names=movieHeader)
ratingsData = pd.read_csv('ml-1m/ratings.dat', sep='::', engine='python', header=None, names=ratingsHeader)
userData = pd.read_csv('ml-1m/users.dat', sep='::', engine='python', header=None, names=userHeader)


# A) ACCEPT INPUT
# This is in a method to permaloop until we get a proper input
def get_user_id_from_console() -> int:
    chosenUserId = None
    while chosenUserId is None or chosenUserId < 1 or chosenUserId > 6040:
        try:
            print('Chose a userId:')
            chosenUserId = int(input())
            if chosenUserId < 1 or chosenUserId > 6040:
                print('INVALID INPUT')

        except ValueError:
            print('INVALID INPUT')

    return chosenUserId


# B) print 15 movies the user Rated
def print15ratedmovies() -> None:
    # Get 15 random movies (all rated 20+ according to readme)
    random_rated_movie = ratingsData.query('UserId==' + str(currentUserId)).sample(n=15)
    # mergeWithMovie
    random_rated_movie = random_rated_movie.merge(movieData, on='MovieId')
    # Print only the requested stuff
    print(random_rated_movie[['Title', 'Genre']].to_string(index=False))


# DECIDER VARIABLES
neighbors_amount = 20
movies_suggested = 10
rating_threshhold = 3  # Needs x votes to count towards suggestions(gets lowered if not enough movies get found)
min_rating = 3


# get cosine neighbors
# sum of rating per movie where rating user1*rating user2 devided by the vecotorized user1*user2
# vectorized user: root of the sum of the ratings squared
def get_cosine_neighbors(ratingsData, currentRatedMovies, currentUserId) -> pd.DataFrame:
    currentUserVector = ((currentRatedMovies['Ratings'] ** 2).sum()) ** (1 / 2)
    pivoted_ratings = pd.pivot_table(ratingsData, values='Ratings', index=['MovieId'], columns=['UserId'], fill_value=0)
    # create sum of(Rx*Ry) series
    pivoted_ratings_sum = pivoted_ratings.multiply(pivoted_ratings[currentUserId], axis='index').sum(axis=0,
                                                                                                     skipna=True)
    # create vectors list
    pivoted_ratings_vectors = ((pivoted_ratings ** 2).sum(axis=0, skipna=True)) ** (1 / 2)
    pivoted_ratings_vectors = pivoted_ratings_vectors.multiply(currentUserVector)
    neighs = pivoted_ratings_sum.divide(pivoted_ratings_vectors)
    neighs.drop(neighs.index[currentUserId - 1], inplace=True)
    neighs = neighs.nlargest(neighbors_amount)
    return pd.DataFrame({'UserId': neighs.index, 'Distance': neighs.values})


# V4: v3, only drops movies with <min_rating too
def get_movie_recommendation(movieData, ratingsData, currentRatedMovies, neighs) -> pd.DataFrame:
    neighborRatings = pd.merge(ratingsData[['UserId', 'MovieId', 'Ratings']], neighs[neighbors_header], on='UserId')
    # remove ratings under the min_rating threshhold
    neighborRatings = neighborRatings[neighborRatings.Ratings > min_rating]
    # ratings*weighted distance
    neighborRatings['WeightedRating'] = neighborRatings['Ratings'] * neighborRatings['Distance']
    # Keep only important columns
    neighborRatings = neighborRatings[['MovieId', 'WeightedRating']]
    # remove movies the user rated
    curMovIDs = currentRatedMovies['MovieId']
    neighborRatings = neighborRatings.query('MovieId not in @curMovIDs')
    # remove movies under threshhold
    dropMovies = neighborRatings[['MovieId', 'WeightedRating']].groupby(['MovieId'], as_index=False).filter(
        lambda x: x['WeightedRating'].count() <= rating_threshhold)
    dropMovies = dropMovies['MovieId']
    neighborRatings = neighborRatings.query('MovieId not in @dropMovies')
    moviesAvgRating = neighborRatings[['MovieId', 'WeightedRating']].groupby(['MovieId'], as_index=False).agg('mean')
    # Get n best rated movies
    xSuggestedMovies = moviesAvgRating.nlargest(movies_suggested, 'WeightedRating')
    xMovieIds = xSuggestedMovies['MovieId']
    return movieData.query('MovieId in @xMovieIds')


def recommender(movieData, ratingsData, userId) -> pd.DataFrame:
    currentRatedMovies = ratingsData.query('UserId==' + str(userId))
    neighbors = get_cosine_neighbors(ratingsData, currentRatedMovies, userId)
    return get_movie_recommendation(movieData, ratingsData, currentRatedMovies, neighbors)


# Choose the user
currentUserId = get_user_id_from_console()
# Get movies the user rated (needed later on too, to remove the movies from the suggestions, because rated == seen)
print15ratedmovies()
# deciding which algorithm to use
movieSuggestions = recommender(movieData, ratingsData, currentUserId)
print(movieSuggestions[['Title', 'Genre']])
