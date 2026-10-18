from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """Custom pagination class to limit the number of objects returned"""
    default_limit = 10
    max_limit = 100
    limit_query_param = "limit"
    offset_query_param = "offset"


class CustomPageNumberPagination(PageNumberPagination):
    """Custom pagination class to paginate"""
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100
    page_query_param = "page"
