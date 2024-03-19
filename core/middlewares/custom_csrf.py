from django.shortcuts import redirect


class CustomCSRFMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 403 and "CSRF verification failed" in response.content.decode("utf-8"):
            # CSRF verification failed during login, redirect to login page
            return redirect("users:login_user")
        return response
