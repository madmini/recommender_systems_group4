import numpy as np
from pandas import DataFrame, Series


class Recommender:
    """
    A content-based, popularity-aware movie recommender system.

    Based on similarity of movies based on their genres.
    """

    ratings: DataFrame
    " A pandas.DataFrame containing ratings. With multi-index (user, movie). "

    movie_genres: DataFrame
    " A pandas.DataFrame containing movie genres as a dummy matrix. "

    rating_colname: str
    " The column name for the rating in the ratings DataFrame. "

    movie_id_colname: str
    " The column name for the movie_id in the movie_genres and ratings DataFrames. "

    popularity: Series = None
    " A pandas.Series containing the number of ratings for each movie. Calculated as needed. "

    def __init__(self, movie_genres: DataFrame, ratings: DataFrame, rating_colname: str, movie_id_colname: str):
        self.ratings = ratings
        self.movie_genres = movie_genres
        self.rating_colname = rating_colname
        self.movie_id_colname = movie_id_colname

    def recommend_movies(self, target_user_id: int, n_recommendations: int = 10, method: int = 4) -> Series:
        """
        Recommends movies for a given user based on similarity to the user's rated movies in terms of genre-overlap.

        :param method: the method to use. corresponds to sub-points of assignment 4.C
        :param target_user_id: the id of the user to find recommendations for
        :param n_recommendations: the number of recommendations requested
        :return: a sorted pandas.Series containing the recommendations
        """

        # the target user's ratings. use .loc[], as the UserID is the primary index of the DataFrame
        user_ratings: Series = self.ratings.loc[target_user_id][self.rating_colname]

        # step 1: create user profile

        # genre count is only available in 4)
        use_genre_count: bool = method >= 4
        user_profile: Series = self.get_user_profile(user_ratings, use_genre_count=use_genre_count)

        # step 2: get overlap
        overlap: Series = self.get_overlap(user_profile)

        # step 3: filter movies
        score: Series
        if method == 2:
            # sort by overlap count
            score = overlap

        elif method <= 4:
            # sort by popularity
            score = self.get_popularity()

        else:
            # custom method, sort by popularity AND user profile

            # multiply the user_profile to the movie_genres to include the genre count into the score
            weighted_genres: DataFrame = self.movie_genres * user_profile
            # for each movie, calculate the mean of all genre scores
            # to get a measure of how similar the movie is to the user's profile
            #   set zero-values to np.nan, so they are not included in the calculation
            genre_similarity = weighted_genres.replace(0, np.nan).mean(axis='columns')
            # multiply with the popularity to get a measure that includes both
            score = self.get_popularity() * genre_similarity

        # step 4: filter, sort and return

        # a filter, specifying which movies a user has not yet rated
        #  '~' is the bitwise NOT operator, overridden for numpy.ndarray such that NOT is applied to each value
        #  this inverts the list from "movies that the user has rated" to "movies that the user has not rated"
        not_yet_rated = ~ self.movie_genres.index.isin(user_ratings.index)

        # only select movies that the user has not rated yet AND for which the overlap is greater than zero
        #  select the n largest values (faster than sort)
        #  use keep='all' so that movies with identical score are not removed
        #  however using keep='all' can result in more than n values, thus trim again
        return score[not_yet_rated & (overlap > 0)].nlargest(n_recommendations, keep='all').head(n_recommendations)

    def get_user_profile(self, user_ratings: Series, use_genre_count: bool = False) -> Series:
        """
        Generate a user profile listing genres that the user "likes".

        A genre is considered to be "liked" if at least one rated movie contains it.
        If use_genre_count is True, a genre has to appear in the ratings with above average frequency.

        :param user_ratings: the ratings of the target user
        :param use_genre_count: whether or not to account for the number of ratings
        :return: a boolean array of genres, determining whether the user "likes" the genre
        """

        # filter rated movies by ratings
        liked_movies_filter = self.filter_user_ratings(user_ratings)
        filtered_movies = self.movie_genres.loc[liked_movies_filter]

        user_profile: Series
        if use_genre_count:
            # the number of ratings in which each genre appears
            genre_count: Series = filtered_movies.sum()
            # remove all genres that have below average genre counts
            genre_count[genre_count < genre_count.mean()] = 0
            user_profile = genre_count
        else:
            # the genres that appear in the user's ratings
            user_profile = filtered_movies.any()

        return user_profile

    @staticmethod
    def filter_user_ratings(user_ratings: Series) -> Series:
        """
        Generate a movie filter based on a single user's ratings.

        :param user_ratings: a pandas.DataFrame of ratings for a single user
        :return: the filtered user ratings
        """

        # select all positive ratings (all ratings that are above average)
        #  this generates a boolean list indicating whether each rated movie was rated positively
        positive_ratings: Series = user_ratings >= user_ratings.mean()
        # get the MovieIDs from positively rated movies by applying the boolean array to itself, then getting the index
        return positive_ratings[positive_ratings].index

    def get_overlap(self, user_profile: Series) -> Series:
        """
        Count the number of genres each movie has in common with the user profile.

        :param user_profile: a pandas.Series of genres with scores; a score above zero is considered as positive
        :return: a pandas.Series of movies with overlap counts
        """

        # selects only the genres the user "likes"
        selected_genres = self.movie_genres.loc[:, user_profile > 0]

        # calculate overlap as sum of genres
        return selected_genres.sum(axis='columns')

    def get_popularity(self) -> Series:
        """
        Count number of ratings for each movie.

        :return: a pandas.Series listing the number of ratings for each movie_id
        """

        # only calculate popularity if it is not yet present
        if self.popularity is None:
            # group ratings by movie
            #  select one column, as pandas will count values for each column
            #  it does not matter which column is selected
            movies = self.ratings[self.rating_colname].groupby(self.movie_id_colname)
            # calculate number of ratings in each group (for each movie)
            self.popularity = movies.count()

        return self.popularity
