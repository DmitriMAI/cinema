import elasticsearch
from typing import Optional

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

def es_create_index_if_not_exists(es, index):
    try:
        es.indices.create(index=index)
    except elasticsearch.exceptions.RequestError as ex:
        if ex.error != 'resource_already_exists_exception':
            raise ex

es_create_index_if_not_exists(es, "movies")


def filter_movies(
    name: Optional[str] = None,
    actors: Optional[str] = None,
    genre: Optional[str] = None,
    date: Optional[str] = None,
    from_: int = 0,
    size: int = 10
):
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

    res = es.search(index="movies", body=query, from_=from_, size=size)
    return res["hits"]["hits"]
