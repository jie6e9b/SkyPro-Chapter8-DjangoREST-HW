from rest_framework import serializers
from urllib.parse import urlparse


def validate_video_url_only_youtube(value):
    """
    Отдельный валидатор (функция), который можно переиспользовать.
    """
    parsed_url = urlparse(value)
    domain = parsed_url.netloc.lower()

    allowed_domains = ["www.youtube.com", "youtube.com", "youtu.be"]

    if domain not in allowed_domains:
        raise serializers.ValidationError("Можно добавлять только ссылки на YouTube.")
    return value
