from django.core.cache import cache
from django.http import JsonResponse, HttpResponseForbidden
from functools import wraps

def rate_limit(key_prefix, limit, period):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Use IP address as identifier for unauthenticated users, user ID for authenticated
            identifier = str(request.user.id) if request.user.is_authenticated else request.META.get('REMOTE_ADDR', 'unknown')
            cache_key = f"rl_{key_prefix}_{identifier}"
            
            requests = cache.get(cache_key, 0)
            if requests >= limit:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                    return JsonResponse({'error': 'Rate limit exceeded. Please try again later.'}, status=429)
                return HttpResponseForbidden("Rate limit exceeded. Please try again later.")
            
            cache.set(cache_key, requests + 1, period)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
