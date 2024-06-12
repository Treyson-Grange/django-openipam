import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.http import require_POST


@require_POST
def login_request(request):
    try:
        if request.content_type != "application/json":
            return JsonResponse(
                {"detail": "Invalid content type, expecting application/json"},
                status=400,
            )

        data = json.loads(request.body)
        username = data.get("username", None)
        password = data.get("password", None)

        if username is None or password is None:
            return JsonResponse(
                {"detail": "Please provide both username and password"}, status=400
            )

        user = authenticate(username=username, password=password)
        if user is None:
            return JsonResponse({"detail": "Invalid Credentials"}, status=401)

        login(request, user)
        return JsonResponse(
            {
                "username": user.username,
                "email": user.email,
                "id": user.id,
            },
            status=200,
        )
    except json.JSONDecodeError as e:
        return JsonResponse({"detail": "Invalid JSON format", "error": e}, status=400)
    except Exception as e:
        return JsonResponse({"detail": "Internal Server Error", "error": e}, status=500)


@require_POST
def logout_request(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Not logged in"}, status=400)

    logout(request)
    return JsonResponse({"detail": "Logged out"}, status=200)


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
