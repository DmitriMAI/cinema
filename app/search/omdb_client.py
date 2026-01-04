import os
import requests
import logging

logger = logging.getLogger(__name__)

OMDB_BASE_URL = os.getenv("OMDB_BASE_URL", "http://www.omdbapi.com/")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

def get_movie_poster(name: str):
    if not OMDB_API_KEY:
        logger.error("OMDB_API_KEY переменная не установлена, возвращаем пустой адрес постера фильма")
        return ""

    logger.info("Запрос адреса постера фильма из OMDb", extra={"movie_name": name})

    try:
        res = requests.get(
            OMDB_BASE_URL,
            params={
                "apikey": OMDB_API_KEY,
                "t": name
            },
            timeout=5
        )
        data = res.json()
        poster = data.get("Poster", "")

        if not poster:
            logger.info(
                "Poster не найден в ответе OMDb",
                extra={"movie_name": name}
            )

        return poster

    except Exception:
        logger.error(
            "Ошибка получения адреса постера фильма из OMDb",
            extra={"movie_name": name},
            exc_info=True
        )
        return ""
