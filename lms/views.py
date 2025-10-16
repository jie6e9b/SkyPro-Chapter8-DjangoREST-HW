from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import IntegrityError

from lms.models import Course, Lesson,CourseSubscription
from lms.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner
from .serializers import CourseSubscriptionSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .paginators import CoursePaginator, LessonPaginator

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator
    
    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ["update", "partial_update", "retrieve"]:
            self.permission_classes = [IsAuthenticated, (IsModerator | IsOwner)]
        elif self.action == "destroy":
            self.permission_classes = [IsAuthenticated, ~IsModerator & IsOwner]
        elif self.action == "list":
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = Course.objects.all().order_by("id")
        # For list action, restrict non-moderators to their own objects.
        if getattr(self, "action", None) == "list":
            if self.request.user.groups.filter(name="Moderators").exists():
                return qs
            return qs.filter(owner=self.request.user)
        # For retrieve/update/destroy, return full queryset so permissions yield 403 (not 404).
        return qs


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator
    
    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ["update", "partial_update", "retrieve"]:
            self.permission_classes = [IsAuthenticated, (IsModerator | IsOwner)]
        elif self.action == "destroy":
            self.permission_classes = [IsAuthenticated, ~IsModerator & IsOwner]
        elif self.action == "list":
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        qs = Lesson.objects.all().order_by("id")
        if getattr(self, "action", None) == "list":
            if self.request.user.groups.filter(name="Moderators").exists():
                return qs
            return qs.filter(owner=self.request.user)
        return qs


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def subscribe_to_course(request, course_id):
    try:
        # Проверяем существование курса
        course = Course.objects.get(id=course_id)
        
        # Проверяем существование подписки
        if CourseSubscription.objects.filter(user=request.user, course=course).exists():
            return Response(
                {"detail": "Вы уже подписаны на этот курс"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        subscription = CourseSubscription.objects.create(
            user=request.user, course=course
        )
        serializer = CourseSubscriptionSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Course.DoesNotExist:
        return Response({"detail": "Курс не найден"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def unsubscribe_from_course(request, course_id):
    try:
        subscription = CourseSubscription.objects.get(
            user=request.user, course_id=course_id
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except CourseSubscription.DoesNotExist:
        return Response(
            {"detail": "Подписка не найдена"}, status=status.HTTP_404_NOT_FOUND
        )


class CourseSubscriptionView(APIView):
    def post(self, request, *args, **kwargs):
        course_id = request.data.get('course')
        course_item = get_object_or_404(Course, id=course_id)
        
        # Проверяем существование подписки
        subs_item = CourseSubscription.objects.filter(
            user=request.user,
            course=course_item
        )
        
        # Если подписка существует - удаляем
        if subs_item.exists():
            subs_item.delete()
            message = 'Подписка удалена'
        # Если подписки нет - создаем
        else:
            CourseSubscription.objects.create(
                user=request.user,
                course=course_item
            )
            message = 'Подписка добавлена'
            
        return Response({"message": message})