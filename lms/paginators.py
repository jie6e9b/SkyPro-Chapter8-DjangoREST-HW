
from rest_framework.pagination import PageNumberPagination


class CoursePaginator(PageNumberPagination):
    page_size = 10  # количество элементов на странице
    page_size_query_param = 'page_size'  # параметр для указания количества элементов в запросе
    max_page_size = 50  # максимальное количество элементов на странице


class LessonPaginator(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100
