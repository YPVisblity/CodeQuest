from django.shortcuts import redirect


class StaffAdminAccessMiddleware:
    """Only signed-in staff members may access Django's admin routes."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        is_admin_path = request.path == "/admin" or request.path.startswith("/admin/")

        if is_admin_path and not (
            request.user.is_authenticated and request.user.is_staff
        ):
            return redirect("/?view=map")

        return self.get_response(request)
