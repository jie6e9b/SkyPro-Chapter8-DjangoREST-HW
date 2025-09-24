from django.contrib import admin
from django.contrib.auth.decorators import permission_required
from django.urls import include, path

from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from lms.views import CourseViewSet, LessonViewSet
from users.views import PaymentViewSet, UserCreateAPIView, UserUpdateAPIView

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"lessons", LessonViewSet, basename="lesson")
router.register(r"payments", PaymentViewSet, basename="payment")


urlpatterns = [
    path("admin/", admin.site.urls),
    # API через DRF Router
    path("api/", include(router.urls)),
    # Пользователи
    path("users/<int:pk>/", UserUpdateAPIView.as_view(), name="register"),
    path("users/register/", UserCreateAPIView.as_view(), name="user-update"),
    # настройка авторизации  Simple JWT:
    path(
        "users/login/",
        TokenObtainPairView.as_view(permission_classes=(AllowAny,)),
        name="login",
    ),
    path(
        "users/token/refresh/",
        TokenRefreshView.as_view(permission_classes=(AllowAny,)),
        name="token_refresh",
    ),
]
