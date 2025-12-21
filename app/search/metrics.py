from prometheus_client import Counter

SEARCH_REQUESTS = Counter(
    'search_requests_total',
    'Total number of search requests'
)

MOVIE_VIEWS = Counter(
    'movie_views_total',
    'Total number of movie views',
    ['movie_name']
)
