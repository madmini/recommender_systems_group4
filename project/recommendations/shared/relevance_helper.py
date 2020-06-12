from util import data_helper

# returns relative value for the difference in release years
def get_year_relevance(movie_id:int):
    release_years= data_helper.get_releaseyears()
    movie_year=release_years.loc[movie_id]
    release_years = release_years.subtract(movie_year)
    release_years = release_years.abs()
    release_years=release_years.div(release_years.max())
    return release_years.drop(movie_id)

# returns relative value for the genre-overlap (1 = same genres, missing genres decrease the value)
# is at least first_overlap_value, if 1 genre overlaps
# this is to rate the first genre higher compared to multiple overlaps
def get_genre_overlap_values(movie_id:int,first_overlap_value:float=0.5):
    genres= data_helper.get_genre_as_lists().to_frame()
    movie_genres = genres['genres'].loc[movie_id]
    genres['overlap']=genres['genres'].apply(lambda x: [value for value in x if value in movie_genres])
    # divide by amount of genres and scale it according tot he parameters
    genres['result']=genres['overlap'].apply(lambda x: (len(x) * (1 - first_overlap_value) )/ len(movie_genres))
    genres['result']=genres['result'].apply(lambda x: x+first_overlap_value if x > 0 else x)
    return genres['result'].drop(movie_id)