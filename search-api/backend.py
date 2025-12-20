from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import Response
import elasticsearch
import requests
import csv
import traceback
from typing import Optional
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
import time


app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Счетчик поисковых запросов
SEARCH_REQUESTS = Counter('search_requests_total', 'Total number of search requests')

# Prometheus метрики
# Счетчик просмотров фильмов по названию
MOVIE_VIEWS = Counter('movie_views_total', 'Total number of movie views', ['movie_name'])

@app.get("/metrics")
async def metrics():
    """Эндпоинт для сбора метрик Prometheus"""
    # Используем Response с правильным content-type
    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain"
    )

def es_create_index_if_not_exists(es, index):
    """Create the given ElasticSearch index and ignore error if it already exists"""
    try:
        es.indices.create(index=index)
    except elasticsearch.exceptions.RequestError as ex:
        if ex.error == 'resource_already_exists_exception':
            pass  # Index already exists. Ignore.
        else:  # Other exception - raise it
            raise ex

def insert_movies(filename):
    # open the CSV file and read the rows
    with open(filename, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # extract the movie data from the row
            movie = {
                "name": row["movie_title"],
                "actors": row["actor_1_name"],
                "genre": row["genres"],
                "release_date": row["title_year"]
            }

            # insert the movie into the Elasticsearch index
            es.index(index="movies", body=movie)

# Elasticsearch connection with compatibility settings
es = elasticsearch.Elasticsearch(
    # если оч хотим локально
    # ["http://localhost:9200"],
    # Для докера, либо если в одной сети
    ["http://elasticsearch:9200"],

    # Хммм, сломалось
    # ["http://0.0.0.0:9200"]
    # Добавляем параметры для совместимости
    verify_certs=False,
    request_timeout=30,
)
es_create_index_if_not_exists(es, "movies")
# insert_movies("movie_metadata.csv")  # Раскомментируйте после исправления ошибки

def filter_movies(name: Optional[str] = None, 
                  actors: Optional[str] = None, 
                  genre: Optional[str] = None, 
                  date: Optional[str] = None):
    query = {
        "query": {
            "bool": {
                "must": []
            }
        }
    }

    if name:
        query["query"]["bool"]["must"].append({
            "match": {
                "name": name
            }
        })
    if actors:
        query["query"]["bool"]["must"].append({
            "match": {
                "actors": actors
            }
        })
    if genre:
        query["query"]["bool"]["must"].append({
            "match": {
                "genre": genre
            }
        })
    if date:
        query["query"]["bool"]["must"].append({
            "match": {
                "release_date": date
            }
        })

    res = es.search(index="movies", body=query)
    return res["hits"]["hits"]

def get_movie_poster(name: str):
    # make a GET request to the OMDb API to get the movie poster
    res = requests.get(
        "http://www.omdbapi.com/",
        params={
            "apikey": "74e22e02",
            "t": name
            # Убрал "i": "tt3896198" так как это конкретный ID фильма
        }
    )

    # extract the movie poster URL from the response
    try:
        print(res.json())
        data = res.json()
        poster_url = data.get("Poster", "")
    except Exception as e:
        error_message = traceback.format_exc()
        print(error_message)
        poster_url = ""

    return poster_url

@app.get("/search")
async def search(
    name: Optional[str] = Query(None),
    actors: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    date: Optional[str] = Query(None)
):
    print("in search")
    SEARCH_REQUESTS.inc()
    try:
        # filter the movies
        movies = filter_movies(name, actors, genre, date)

        # get the movie posters
        for movie in movies:
            movie_name = movie["_source"]["name"]
            MOVIE_VIEWS.labels(movie_name=movie_name).inc()
            movie["_source"]["poster_url"] = get_movie_poster(movie["_source"]["name"])

        return {
            "hits": {
                "hits": movies
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/poster")
async def poster(name: str = Query(...)):
    try:
        # get the movie poster URL
        poster_url = get_movie_poster(name)
        return poster_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/insert")
async def insert(movie_data: dict):
    try:
        # insert the movie into Elasticsearch
        res = es.index(index="movies", body=movie_data)

        return {
            "result": "success",
            "id": res["_id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Movie Search API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)