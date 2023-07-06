from django.http import HttpResponseForbidden

def admin_required(view_func):
    """
    Decorator function to check if the user is an admin.
    """
    def wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated or not user.is_staff:
            return HttpResponseForbidden('You are not authorized to access this page.')
        return view_func(request, *args, **kwargs)
    return wrapped_view