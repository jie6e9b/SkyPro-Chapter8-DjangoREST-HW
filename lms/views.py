from rest_framework import viewsets, filters
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer

class CourseViewSet(viewsets.ModelViewSet):
    """
    CRUD для курсов.
    list, create, retrieve, update, destroy.
    Фильтрация и поиск по имени.
    """
    queryset = Course.objects.prefetch_related('lessons').all()
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']


class LessonViewSet(viewsets.ModelViewSet):
    """
    CRUD для уроков.
    list, create, retrieve, update, destroy.
    Фильтрация по имени и курсу через query params:
    ?course=<id>
    """
    serializer_class = LessonSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'course__name']
    ordering_fields = ['name']

    def get_queryset(self):
        """
        Если указан query param 'course', фильтруем уроки по курсу.
        """
        queryset = Lesson.objects.select_related('course').all()
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset