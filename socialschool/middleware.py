from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # List of URL patterns that don't require login
        self.public_urls = [
            '/accounts/login/',
            '/accounts/logout/',
            '/accounts/register/',
            '/admin/',
            '/accounts/password_reset/',
            '/accounts/password_reset/done/',
            '/accounts/reset/<uidb64>/<token>/',
            '/accounts/reset/done/',
        ]

    def __call__(self, request):
        if not request.user.is_authenticated:
            # Check if the requested URL is in public URLs
            if not any(request.path.startswith(url) for url in self.public_urls):
                # Redirect to login page with next parameter
                return redirect(f"{reverse('login')}?next={request.path}")
        response = self.get_response(request)
        return response
