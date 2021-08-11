import csv

import json
import time
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from model import API_KEY
from model.recommend_model import recommendation
import tmdbsimple as tmdb


def get_image_url(movie_name):
    tmdb.API_KEY = API_KEY.api_key
    search = tmdb.Search()
    response = search.movie(query=movie_name)
    image_url = response['results'][0]['poster_path']
    image_url = "https://image.tmdb.org/t/p/w600_and_h900_bestv2" + image_url
    return image_url


def get_similar_movies_poster(recommend_movies):
    recommend_poster_images = []
    for movie in recommend_movies:
        recommend_poster_images.append(get_image_url(movie))
    return recommend_poster_images


def get_cast_info(movie_id):
    movie = tmdb.Movies(movie_id)
    credits = movie.credits()

    print(credits['cast'][0])
    actor_temp = []
    actor_info = {
        'known_for_department': [], 'name': [], 'profile_path': [], 'character': []
    }
    i = 0
    for temp in credits['cast']:
        if i == 8:
            break
        try:
            name = temp['known_for_department'] + "|" + temp["name"] + "|" + temp["profile_path"] + "|" + temp[
                "character"]
            actor_temp.append(temp)
        except:
            continue
        i = i + 1
    return actor_temp


def get_genre_info(movie_genre_list):
    # movie_genre_list = search.results[0]['genre_ids']

    genres = tmdb.Genres()
    genres_list = genres.movie_list()

    genre_names = []
    for temp in genres_list['genres']:
        if temp['id'] in movie_genre_list:
            genre_names.append(temp['name'])

    # print(genre_names)
    return genre_names


def index(request):
    if request.method == "POST":
        tick = time.time()
        movie_name = request.POST.get('moviename').lower()
        movie_list = recommendation(str(movie_name))
        # movie_list = recommendation_read_npy(str(movie_name))
        print(movie_list)
        if movie_list is None:
            return render(request, 'index.html', {'not_found': 'The movie is not in our database'})

        """   Movie Search   """

        movie_list = list(movie_list[1:9])
        tmdb.API_KEY = API_KEY.api_key
        search = tmdb.Search()
        response = search.movie(query=movie_name)
        movie_id = search.results[0]['id']
        async_time_start = time.time()
        # Movie Info
        movie_info = response['results'][0]

        # Cast Info
        cast_info = get_cast_info(movie_id)

        # Genre Info
        genre_info = get_genre_info(search.results[0]['genre_ids'])

        # Searched Movie Poster
        image_url = get_image_url(movie_name)

        # Similiar Movie Posters
        similiar_posters = get_similar_movies_poster(movie_list)

        movies_with_posters = []
        for i in range(0, len(similiar_posters)):
            temp = [movie_list[i], similiar_posters[i]]
            movies_with_posters.append(temp)
        async_time_end = time.time()
        context = {
            'movies_with_posters': movies_with_posters,
            'movies': movie_list,
            'image': image_url,
            'movie_info': movie_info,
            'cast_info': cast_info,
            'genre_info': genre_info,
            'similiar_posters': similiar_posters,
            'time_taken': time.time() - tick,
            'async_time_taken': async_time_end - async_time_start,

        }

        return render(request, 'index.html', context)
    return render(request, 'index.html', {})


def autocomplete(request):
    if request.method == 'GET':
        term = request.GET.get('term')
        movie_names = get_movie_names()
        if term:
            len_term = len(term)
            ans = []
            for x in movie_names:
                if term in x[0:len_term].lower():
                    ans.append(x)
            return JsonResponse(ans, safe=False)
    pass


def json_read(request):
    if request.method == 'POST':
        f = open("C:\DEV\Django\MovieRecommendation\sample.json", )
        context = json.load(f)

        return render(request, 'index.html', context)


def get_movie_names():
    f = open('model/movie.csv', encoding='utf8')
    i = 0
    movie_names = []
    try:
        for line in csv.DictReader(f):
            try:
                movie_names.append(line['movie_title'])
            except:
                i += 1
    except Exception as e:
        print(e)
        i += 1

    return movie_names
