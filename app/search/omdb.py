import requests
import traceback

def get_movie_poster(name: str):
    res = requests.get(
        "http://www.omdbapi.com/",
        params={
            "apikey": "74e22e02",
            "t": name
            # Убрал "i": "tt3896198" так как это конкретный ID фильма
        }
    )

    try:
        print(res.json())
        data = res.json()
        poster_url = data.get("Poster", "")
    except Exception as e:
        error_message = traceback.format_exc()
        print(error_message)
        poster_url = ""

    return poster_url