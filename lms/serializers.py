from rest_framework.fields import SerializerMethodField
from rest_framework import serializers
from .models import Course, Lesson

class LessonGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['name']

class CourseSerializer(serializers.ModelSerializer):

    lessons_count = serializers.SerializerMethodField()
    lessons_group = LessonGroupSerializer(source='lessons', many=True, read_only=True)

    class Meta:
        model = Course
        fields = ('name', 'preview', 'description', 'lessons_count', 'lessons_group')

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

