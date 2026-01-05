import uuid
import jwt
import datetime
from django.conf import settings
from django.utils import timezone
from .models import User, RefreshToken


class JWTManager:
    """Менеджер для работы с JWT токенами"""

    def __init__(self, secret_key=None, algorithm='HS256'):
        self.secret_key = secret_key or settings.SECRET_KEY
        self.algorithm = algorithm

    def create_access_token(self, user, expires_in_hours=settings.ACCESS_TOKEN_LIFETIME_HOURS):
        """Создает JWT access токен"""
        payload = {
            'user_id': str(user.username),
            'email': user.email,
            'role': user.role.name if user.role else None,
            'exp': timezone.now() + datetime.timedelta(hours=expires_in_hours),
            'iat': timezone.now(),
            'type': 'access',
            'jti': str(uuid.uuid4()),
        }

        token = jwt.encode(
            payload=payload,
            key=self.secret_key,
            algorithm=self.algorithm
        )
        return token

    def verify_access_token(self, token):
        """Проверяет и декодирует JWT access токен"""
        try:
            payload = jwt.decode(
                jwt=token,
                key=self.secret_key,
                algorithms=[self.algorithm]
            )

            if payload.get('type') != 'access':
                raise ValueError("Invalid token type")

            return payload

        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e}")

    def get_user_from_access_token(self, token):
        """Получает пользователя из JWT токена"""
        try:
            payload = self.verify_access_token(token)
            user = User.objects.get(
                username=payload['user_id'], is_active=True)
            return user
        except (ValueError, User.DoesNotExist, KeyError) as e:
            print(f"Error getting user from token: {e}")
            return None

    def create_tokens_for_response(self, user, response):
        """Создает токены и добавляет их в куки ответа"""
        access_token = self.create_access_token(user)
        refresh_token = RefreshToken.create_token(user)

        # Устанавливаем куки
        response.set_cookie(
            'access_token',
            access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Strict',
            max_age=settings.ACCESS_TOKEN_LIFETIME_HOURS *
            60*60,  # 1 час (исправлено с 60 секунд)
        )

        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Strict',
            max_age=settings.REFRESH_TOKEN_LIFETIME_DAYS * 24*3600,  # 30 дней
        )

        return response

    def refresh_access_token_with_rotation(self, refresh_token_str):
        """Создает новый access token с ротацией refresh токена"""
        # Ротация токена (создает новый, отзывает старый)
        new_refresh_token = RefreshToken.rotate_token(refresh_token_str)

        if not new_refresh_token:
            raise ValueError("Invalid or expired refresh token")

        # Получаем новый refresh token объект
        rt = RefreshToken.objects.get(token=new_refresh_token, is_active=True)

        # Создаем новый access token
        new_access_token = self.create_access_token(rt.user)

        return new_access_token, new_refresh_token, rt.user


jwt_manager = JWTManager()
