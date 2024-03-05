from rest_framework import pagination
from rest_framework.pagination import LimitOffsetPagination


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 1000


class Pagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100
