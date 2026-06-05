from .models import User
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.cache import cache


# serializer for a general login
class RedisTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        cache.set(
            f"user_session_{user.id}",
            {
                "id": user.id,
                "email": user.email,
            },
            timeout=3600,
        )

        return data


# serializer for swagger login
class EmailTokenObtainSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):

        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        cache.set(
            f"user_session_{user.id}",
            {
                "id": user.id,
                "email": user.email,
            },
            timeout=3600,
        )

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


# serializer for sing up перепишу
class EmailValidationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    code = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "code", "password", "first_name", "last_name"]

    def create(self, validated_data):
        validated_data.pop("code", None)
        return user.objects.create_user(**validated_data)    # type: ignore[attr-defined]
    





# serializer-helper for comment,project,tasks
user = get_user_model()


class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields = ["id", "email", "first_name", "last_name"]