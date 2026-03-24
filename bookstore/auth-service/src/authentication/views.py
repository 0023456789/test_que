import logging
import os

import jwt
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User
from .serializers import RegisterSerializer, UserSerializer, ValidateTokenSerializer

logger = logging.getLogger(__name__)
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "super-secret-jwt-key")


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return JsonResponse({"status": "healthy", "service": "auth-service"})


class RegisterView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        # inject custom claims
        refresh["role"] = user.role
        refresh["email"] = user.email
        refresh["username"] = user.username
        refresh["first_name"] = user.first_name
        refresh["last_name"] = user.last_name

        logger.info(f"New user registered: {user.email} role={user.role}")

        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def validate_token(request):
    """Internal endpoint for API Gateway to validate tokens."""
    serializer = ValidateTokenSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    token = serializer.validated_data["token"]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return Response({"valid": True, "payload": payload})
    except jwt.ExpiredSignatureError:
        return Response({"valid": False, "error": "Token expired"}, status=401)
    except jwt.InvalidTokenError as e:
        return Response({"valid": False, "error": str(e)}, status=401)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """Return current user profile."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_users(request):
    """Admin-only: list all users."""
    if request.user.role not in ["admin", "manager"]:
        return Response({"error": "Forbidden"}, status=403)
    users = User.objects.all()
    return Response(UserSerializer(users, many=True).data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    """Update user profile (self or admin)."""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if str(request.user.id) != str(user_id) and request.user.role != "admin":
        return Response({"error": "Forbidden"}, status=403)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """Blacklist the refresh token."""
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logged out successfully"})
    except Exception as e:
        return Response({"error": str(e)}, status=400)
