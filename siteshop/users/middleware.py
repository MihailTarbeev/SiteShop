from django.utils.deprecation import MiddlewareMixin
from .models import Session, User
from datetime import datetime
from django.utils import timezone


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Получаем сессию из куки
        session_key = request.COOKIES.get('sessionid')
        request.user = None

        if session_key:
            try:
                session = Session.objects.get(
                    session_key=session_key,
                    is_active=True
                )

                # Проверяем не истекла ли сессия
                if timezone.now() < session.expires_at:
                    request.user = session.user
                    request.session = session
            except Session.DoesNotExist:
                pass
