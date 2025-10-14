from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import Course, Lesson, CourseSubscription
from .validators import validate_video_url_only_youtube


class LessonGroupSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(validators=[validate_video_url_only_youtube])
    
    class Meta:
        model = Lesson
        fields = ["name", "video_url"]


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = SerializerMethodField()
    lessons_group = LessonGroupSerializer(
        source="lessons",
        many=True,
        read_only=True,
    )
    is_subscribed = SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "name",
            "preview",
            "description",
            "lessons_count",
            "lessons_group",
            "owner",
            "is_subscribed",
        )

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return obj.subscriptions.filter(user=user).exists()
        return False


class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(validators=[validate_video_url_only_youtube])

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSubscription
        fields = ["id", "user", "course", "created_at"]
        read_only_fields = ["user", "created_at"]