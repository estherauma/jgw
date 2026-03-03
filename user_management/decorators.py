from functools import wraps

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render


def group_required(group_name):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if user.is_superuser or user.groups.filter(
                name=group_name
            ).exists():
                return view_func(request, *args, **kwargs)
            return render(request, "403.html", status=403)
        return _wrapped_view

    return decorator
