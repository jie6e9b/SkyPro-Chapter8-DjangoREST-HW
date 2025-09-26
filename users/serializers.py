from rest_framework import serializers

from .models import Payment, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        email = validated_data.get("email")
        # Создаем username из части email до @
        username = email.split("@")[0]
        # Если такой username существует, добавляем случайные цифры
        if User.objects.filter(username=username).exists():
            from random import randint

            username = f"{username}{randint(1, 9999)}"

        user = User(username=username, **validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "course",
            "lesson",
            "payment_type",
            "payment_price",
            "payment_date",
        ]
