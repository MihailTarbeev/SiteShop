from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .utils import jwt_manager
from siteshop import settings
from .models import User

# class SessionAuthMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         session_key = request.COOKIES.get('sessionid')
#         request.custom_session = None

#         if session_key:
#             try:
#                 custom_session = Session.objects.get(
#                     session_key=session_key,
#                     is_active=True
#                 )

#                 if timezone.now() < custom_session.expires_at:
#                     request.custom_session = custom_session
#                     request.user = custom_session.user
#                 else:
#                     custom_session.is_active = False
#                     custom_session.save()
#             except Session.DoesNotExist:
#                 pass
#         else:
#             request.user = AnonymousUser()


class JWTAuthMiddleware(MiddlewareMixin):
    """
    Middleware для автоматического обновления JWT токенов с ротацией
    """

    def process_request(self, request):
        # Проверяем access token
        access_token = request.COOKIES.get('access_token')

        if access_token:
            try:
                payload = jwt_manager.verify_access_token(access_token)
                # Если токен валиден, получаем пользователя
                from .models import User
                user = User.objects.get(
                    username=payload['user_id'], is_active=True)
                request.user = user
                request.auth_method = 'jwt'
                return  # Все хорошо, токен валиден
            except Exception:
                # Access token невалиден, пробуем обновить
                pass

        # Пробуем обновить токены через refresh token
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token:
            try:
                # Автоматически обновляем с ротацией
                new_access_token, new_refresh_token, user = jwt_manager.refresh_access_token_with_rotation(
                    refresh_token)

                # Сохраняем информацию для установки в куки
                request._new_tokens = {
                    'access_token': new_access_token,
                    'refresh_token': new_refresh_token
                }
                request.user = user
                request.auth_method = 'jwt_refreshed'
                return

            except Exception as e:
                print(f"Error auto-refreshing tokens: {e}")

        # Если дошли сюда, пользователь не аутентифицирован
        request.user = AnonymousUser()
        request.auth_method = None

    def process_response(self, request, response):
        # Если были созданы новые токены, устанавливаем их
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
                max_age=settings.REFRESH_TOKEN_LIFETIME_DAYS * 24*3600,  # 30 дней
            )

        return response
