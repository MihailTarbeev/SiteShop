from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .utils import jwt_manager
from siteshop import settings
from .models import User


class JWTAuthMiddleware(MiddlewareMixin):
    """
    Middleware для автоматического обновления JWT токенов с ротацией
    """

    def process_request(self, request):
        access_token = request.COOKIES.get('access_token')

        if access_token:
            try:
                payload = jwt_manager.verify_access_token(access_token)
                from .models import User
                user = User.objects.get(
                    username=payload['user_id'], is_active=True)
                request.user = user
                request.auth_method = 'jwt'
                return
            except Exception:
                pass

        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token:
            try:
                new_access_token, new_refresh_token, user = jwt_manager.refresh_access_token_with_rotation(
                    refresh_token)

                request._new_tokens = {
                    'access_token': new_access_token,
                    'refresh_token': new_refresh_token
                }
                request.user = user
                request.auth_method = 'jwt_refreshed'
                return

            except Exception as e:
                print(f"Error auto-refreshing tokens: {e}")

        request.user = AnonymousUser()
        request.auth_method = None

    def process_response(self, request, response):
        if hasattr(request, '_new_tokens'):
            response.set_cookie(
                'access_token',
                request._new_tokens['access_token'],
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Strict',
                max_age=settings.ACCESS_TOKEN_LIFETIME_HOURS * 60*60
            )

            response.set_cookie(
                'refresh_token',
                request._new_tokens['refresh_token'],
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Strict',
                max_age=settings.REFRESH_TOKEN_LIFETIME_DAYS * 24*3600,
            )

        return response
