from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve, reverse, Resolver404

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Don't apply to static files or media
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)
            
        # Skip admin paths
        if request.path.startswith('/admin/'):
            return self.get_response(request)
            
        try:
            current_url = resolve(request.path_info).url_name
            # Exempted URLs that don't require login
            exempted_urls = ['login', 'register']
            
            if not request.user.is_authenticated and current_url not in exempted_urls:
                messages.info(request, 'Please log in to access this page.')
                return redirect(f"{reverse('login')}?next={request.path}")
        except Resolver404:
            # If URL doesn't match any pattern, continue
            pass
            
        response = self.get_response(request)
        return response 