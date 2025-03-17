from .models import Activity

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        return response
        
    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None
            
        # Skip tracking for certain paths
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return None
            
        # Log views for specific endpoints if needed
        # This is just an example - you can customize this logic
        if request.method == 'GET' and 'retrieve' in str(view_func):
            try:
                Activity.objects.create(
                    user=request.user,
                    action='VIEW',
                    description=f'Viewed {request.path}',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            except:
                pass  # Don't crash if logging fails
                
        return None
        
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip