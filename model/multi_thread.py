import json
import multiprocessing
import time
import tmdbsimple as tmdb
from django.shortcuts import render

from model import API_KEY
from model.recommend_model import recommendation


def get_cast_info(movie_id, context):
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
    context['cast_info'] = actor_temp


def get_genre_info(movie_genre_list, context):
    # movie_genre_list = search.results[0]['genre_ids']

    genres = tmdb.Genres()
    genres_list = genres.movie_list()

    genre_names = []
    for temp in genres_list['genres']:
        if temp['id'] in movie_genre_list:
            genre_names.append(temp['name'])

    # print(genre_names)
    context['genre_info'] = genre_names


def get_image_url(movie_name):
    tmdb.API_KEY = API_KEY.api_key
    search = tmdb.Search()
    response = search.movie(query=movie_name)
    image_url = response['results'][0]['poster_path']
    image_url = "https://image.tmdb.org/t/p/w600_and_h900_bestv2" + image_url
    return image_url


def get_similar_movies_poster(recommend_movies, movie_list, context):
    recommend_poster_images = []
    for movie in recommend_movies:
        recommend_poster_images.append(get_image_url(movie))
    movies_with_posters = []
    for i in range(0, len(recommend_poster_images)):
        temp = [movie_list[i], recommend_poster_images[i]]
        movies_with_posters.append(temp)
    context['movies_with_posters'] = movies_with_posters


def multi_thread(request):
    if request.method == "POST":
        tick = time.time()
        movie_name = request.POST.get('moviename').lower()
        movie_list = recommendation(str(movie_name))
        print(movie_list)
        if movie_list is None:
            return render(request, 'index.html', {'not_found': 'Not found'})

        """   Movie Search   """

        manager = multiprocessing.Manager()
        context = manager.dict()

        movie_list = list(movie_list[1:9])
        tmdb.API_KEY = API_KEY.api_key
        search = tmdb.Search()
        response = search.movie(query=movie_name)
        # Movie ID
        movie_id = search.results[0]['id']
        # Movie Info
        movie_info = response['results'][0]
        # Cast Info
        p1 = multiprocessing.Process(target=get_cast_info, args=(movie_id, context))
        p1.start()
        p1.join()
        # cast_info = get_cast_info(movie_id)
        # Genre Info
        p2 = multiprocessing.Process(target=get_genre_info,
                                     args=(search.results[0]['genre_ids'], context))
        p2.start()
        p2.join()
        # genre_info = get_genre_info(search.results[0]['genre_ids'])
        # Searched Movie Poster
        image_url = get_image_url(movie_name)
        # Similiar Movie Posters
        p3 = multiprocessing.Process(target=get_similar_movies_poster,
                                     args=(movie_list, movie_list, context))
        p3.start()
        p3.join()
        # similiar_posters = get_similar_movies_poster(movie_list)
        context['image'] = image_url
        context['movie_info'] = movie_info
        context['time_taken'] = time.time() - tick
        context['movie'] = movie_list

        return render(request, 'index.html', dict(context))
    return render(request, 'index.html', {})
