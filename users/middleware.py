from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class UserStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            logout(request)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
                return JsonResponse({"error": "Account deactivated", "ok": False}, status=401)

            messages.error(request, f"Your account has been deactivated. Please contact an administrator.")
            return redirect(settings.LOGIN_URL)

        return self.get_response(request)