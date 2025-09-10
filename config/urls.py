"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from lms.views import CourseViewSet, LessonListCreateAPIView, LessonRetrieveUpdateDestroyAPIView
from users.views import UserUpdateAPIView

router = DefaultRouter()
router.register(r"courses", CourseViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Курсы через ViewSet
    path("api/", include(router.urls)),

    # Уроки через generic views
    path("api/lessons/", LessonListCreateAPIView.as_view(), name="lesson-list-create"),
    path("api/lessons/<int:pk>/", LessonRetrieveUpdateDestroyAPIView.as_view(), name="lesson-detail"),

    # Пользователи (доп. задание)
    path("api/users/<int:pk>/", UserUpdateAPIView.as_view(), name="user-update"),
]