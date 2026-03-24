from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Inject custom claims for RBAC
        token["role"] = user.role
        token["email"] = user.email
        token["username"] = user.username
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        return token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email", "username", "first_name", "last_name",
            "password", "password_confirm", "role",
        ]
        extra_kwargs = {"role": {"default": "customer"}}

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name", "last_name",
            "role", "is_active", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ValidateTokenSerializer(serializers.Serializer):
    token = serializers.CharField()
