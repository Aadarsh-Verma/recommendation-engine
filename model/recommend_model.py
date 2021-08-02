import time
from numpy import asarray
from numpy import save
from numpy import load
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer


def combineFeatures(row):
    return row['director_name'] + " " + row['actor_2_name'] + " " + row['genres'] + " " + row['movie_title'] + " " + \
           row['plot_keywords'] + " " + row['language'] + " " + row['country'] + " " + row['actor_1_name'] + " " + row[
               'actor_3_name'] + " " + row['content_rating']


def recommendation(movie_name):
    tick = time.time()

    df = pd.read_csv('model/movie.csv')
    # df['movie_title'] = df['movie_title'].str.split().str.join(' ')

    exists = False
    for temp in df.movie_title:
        if temp.lower() == movie_name:
            movie_name = temp
            exists = True
    if not exists:
        return None
    cols = ['director_name', 'actor_2_name', 'genres', 'movie_title', 'plot_keywords', 'language', 'country',
            'actor_1_name', 'actor_3_name', 'content_rating']
    df_movies = df.loc[:, cols]

    df_movies.dropna(axis=0, inplace=True)
    df_movies['combined_features'] = df_movies.apply(combineFeatures, axis=1)

    # Adding an index coloumn to the dataset.
    index = np.arange(0, len(df_movies.actor_2_name))
    df_movies['index'] = index
    df_movies.set_index(df_movies['index'], inplace=True)

    # Collaborative Filtering
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(df_movies.combined_features)
    # load array
    # count_matrix = load('count_matrix.npy')
    # print(type(count_matrix))
    # count_matrix
    # print the array
    # print(data)
    # print(type(data))
    cm = count_matrix.toarray()
    # print(type(cm))
    # write_to_txt(cm)
    from sklearn.metrics.pairwise import cosine_similarity
    similarity = cosine_similarity(count_matrix)

    movie_index = df_movies[df_movies['movie_title'] == movie_name]['index'].values[0]
    similiar_movies = list(enumerate(similarity[movie_index]))
    similiar_movies = sorted(similiar_movies, key=lambda x: x[1], reverse=True)

    similiar_movies_top = []
    for i in range(0, 15):
        similiar_movies_top.append(similiar_movies[i])

    similiar_movies_names = []
    for i in similiar_movies_top:
        similiar_movies_names.append(df_movies['movie_title'][i[0]])
    print("cosine similarity time is " + str(time.time() - tick))
    return similiar_movies_names




def write_to_txt(cm):
    # save to npy file
    print("writing data to csv")
    data = asarray(cm)
    print(data)
    save('C:\\DEV\\Django\\MovieRecommendation\\model\\count_matrix.npy', data)
