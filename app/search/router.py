from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from typing import Optional

from app.search.elastic import es, filter_movies
from app.search.metrics import SEARCH_REQUESTS, MOVIE_VIEWS
from app.search.omdb import get_movie_poster
from prometheus_client import generate_latest, REGISTRY

router = APIRouter()

@router.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain"
    )

@router.get("/search")
async def search(
    name: Optional[str] = Query(None),
    actors: Optional[str] = Query(None),
    genre: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
    from_: int = Query(0, alias="from", ge=0),
    size: int = Query(10, ge=1, le=100)
):
    print("in search")
    SEARCH_REQUESTS.inc()

    try:
        movies = filter_movies(
            name=name,
            actors=actors,
            genre=genre,
            date=date,
            from_=from_,
            size=size
        )

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


@router.get("/poster")
async def poster(name: str = Query(...)):
    return get_movie_poster(name)


@router.post("/insert")
async def insert(movie_data: dict):
    res = es.index(index="movies", body=movie_data)
    return {"result": "success", "id": res["_id"]}


@router.get("/")
async def root():
    return {"message": "Movie Search API is running"}
