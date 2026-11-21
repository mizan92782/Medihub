from medihub.models import APIRequestLog

SKIP_PREFIXES = ('/static/', '/media/', '/health', '/metrics', '/favicon')


class APIRequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        path = request.path
        if any(path.startswith(p) for p in SKIP_PREFIXES):
            return response

        try:
            user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
            if ip and ',' in ip:
                ip = ip.split(',')[0].strip()
            APIRequestLog.objects.create(
                path=path[:500],
                method=request.method,
                status_code=response.status_code,
                user=user,
                ip=ip or None,
            )
        except Exception:
            pass

        return response
