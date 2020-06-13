from recommendations import genre_filter


def recommend_movies_filter_genre(movie_id: int, n: int = 5):
    return recommend_movies_genre(movie_id, n)


def recommend_movies_filter_genre_user_bias(movie_id: int, n: int = 5):
    return recommend_movies_genre(movie_id, n, user_bias=True)


def recommend_movies_filter_genre_popularity_bias(movie_id: int, n: int = 5):
    return recommend_movies_genre(movie_id, n, user_bias=True, popularity_bias=True)


def recommend_movies_genre(movie_id: int, n: int = 5, popularity_bias: bool = False, user_bias: bool = False):
    # Get similar movies based on genre
    results = genre_filter.get_movies_with_similar_genres(movie_id, n, popularity_bias, user_bias)

    return results
