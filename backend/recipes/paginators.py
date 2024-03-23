from rest_framework.pagination import (
    LimitOffsetPagination,
    PageNumberPagination,
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'limit'
    max_page_size = 100


class Pagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = 'limit'
    max_limit = 100
