import os
import elasticsearch
import logging
from typing import Optional

logger = logging.getLogger(__name__)

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")

ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "movies")

es = elasticsearch.Elasticsearch(
    [ELASTICSEARCH_URL],
    verify_certs=False,
    request_timeout=30,
)

def es_create_index_if_not_exists(es, index):
    try:
        es.indices.create(index=index)
    except elasticsearch.exceptions.RequestError as ex:
        if ex.error != 'resource_already_exists_exception':
            logger.error("Ошибка создания индекса Elasticsearch", extra={"elastic_index_name": index}, exc_info=True)
            raise

es_create_index_if_not_exists(es, ELASTICSEARCH_INDEX)

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
                "name": name,
                "analyzer": "standard",
                "fuzziness": "AUTO"
            }
        })
    if actors:
        query["query"]["bool"]["must"].append({
            "match": {
                "actors": actors,
                "analyzer": "standard",
                "fuzziness": "AUTO"
            }
        })
    if genre:
        query["query"]["bool"]["must"].append({
            "match": {
                "genre": genre,
                "analyzer": "standard",
                "fuzziness": "AUTO"
            }
        })
    if date:
        query["query"]["bool"]["must"].append({
            "match": {
                "release_date": date
            }
        })

    res = es.search(
        index=ELASTICSEARCH_INDEX,
        body=query,
        from_=from_,
        size=size
    )
    return res["hits"]["hits"]
