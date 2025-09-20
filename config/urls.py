from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from lms.views import CourseViewSet, LessonViewSet
from users.views import UserUpdateAPIView, PaymentViewSet

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"lessons", LessonViewSet, basename="lesson")
router.register(r'payments', PaymentViewSet, basename='payment')


urlpatterns = [
    path("admin/", admin.site.urls),

    # API через DRF Router
    path("api/", include(router.urls)),

    # Пользователи (доп. задание)
    path("api/users/<int:pk>/", UserUpdateAPIView.as_view(), name="user-update"),
]