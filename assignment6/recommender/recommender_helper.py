import pandas as pd
from . import recommender
import json
# the files are from ex. 2 the prepared metadata and the ratings_small (gave new names for easier acces in this task)
# recommender is copied from assignment 3
# movemeta_data is incomplete for some reason -> less results
# for pictures i would do something like this with the link (that isnt working)
def onlygenrenames(genres):
    genre_aslist=eval(genres)
    return [g['name'] for g in genre_aslist]

def onlydirectors(genres):
    genre_aslist=eval(genres)
    return [g['name'] for g in genre_aslist if g['department']=='Directing']

def generate_picture_html(link_end):
    html_string='<img src=\"'
    url='https://image.tmdb.org/t/p/w600_and_h900_bestv2/'+link_end
    html_string=html_string+url+'\" class="movie-picture">'
    return html_string

class recommender_helper:
    user_id_colname = 'UserID'
    movie_id_colname = 'MovieID'
    rating_colname = 'Rating'
    ratings: pd.DataFrame
    metadata: pd.DataFrame
    credits: pd.DataFrame
    def __init__(self):
        self.metadata=pd.read_csv(r'D:\Uni\recommender\Assignments\assignment6\recommender\movies_metadata.csv.xz', encoding='utf8', infer_datetime_format=True)
        self.ratings=pd.read_csv(r'D:\Uni\recommender\Assignments\assignment6\recommender\rating.csv', encoding='utf8',usecols=[self.user_id_colname, self.movie_id_colname, self.rating_colname])
        self.credits=pd.read_csv(r'D:\Uni\recommender\Assignments\assignment6\recommender\credits.csv.xz', encoding='utf8')

    def pretty_recommendations(self, movies):
        movies=movies[['id','title','genres','poster','tagline','overview','cast','crew']]
        movies['genres']=movies['genres'].apply(onlygenrenames)
        return movies
    def get_recommendations(self, user_id):
        return recommender.recommend_movies(ratings=self.ratings, target_user_id=user_id,n_recommendations=20)

    def get_recommendations_with_data(self, user_id):
        movies= self.get_recommendations(user_id)
        movies= self.metadata[self.metadata['id'].isin(movies.index)]
        movies=pd.merge(movies, self.credits,on='id')
        movies['cast'] = movies['cast'].apply(onlygenrenames)
        movies['cast'] = movies['cast'].apply(lambda x: x[:4])
        movies['crew'] = movies['crew'].apply(onlydirectors)
        movies['crew'] = movies['crew'].apply(lambda x: x[:2])
        movies['poster']= movies['poster_path'].apply(generate_picture_html)
        return self.pretty_recommendations(movies)

