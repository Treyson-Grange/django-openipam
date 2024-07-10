import json
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from ..serializers.auth import LoginSerializer
from django.contrib.sessions.middleware import SessionMiddleware


@api_view(["POST"])
@require_POST
@ensure_csrf_cookie
@permission_classes([AllowAny])
def login_request(request):
    if request.content_type != "application/json":
        return Response(
            {"detail": "Invalid content type, expecting application/json"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.validated_data.get("username")
    password = serializer.validated_data.get("password")

    user = authenticate(username=username, password=password)
    if user is None:
        return Response(
            {"detail": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    login(request, user)
    return Response(
        {
            "username": user.username,
            "email": user.email,
            "id": user.id,
        },
        status=status.HTTP_200_OK,
    )


@require_POST
@ensure_csrf_cookie
def logout_request(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Not logged in"}, status=400)

    logout(request)
    return JsonResponse({"detail": "Logged out"}, status=200)


@ensure_csrf_cookie
def whoami(request):
    if not request.user.is_authenticated:
        return JsonResponse({"isAuthenticated": False, "user": None})

    return JsonResponse(
        {
            "isAuthenticated": True,
            "user": {
                "username": request.user.username,
                "email": request.user.email,
                "id": request.user.id,
            },
        }
    )


def get_csrf_token(request):
    session_middleware = SessionMiddleware()
    session_middleware.process_request(request)

    csrf_token = get_token(request)

    if not request.session.session_key:
        request.session.save()

    return JsonResponse(
        {"csrfToken": csrf_token, "session_id": request.session.session_key}
    )
