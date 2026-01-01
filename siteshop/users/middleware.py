from django.utils.deprecation import MiddlewareMixin
from .models import Session, User
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        session_key = request.COOKIES.get('sessionid')
        request.user = get_user(request)
        request.session = None

        if session_key:
            try:
                session = Session.objects.get(
                    session_key=session_key,
                    is_active=True
                )

                if timezone.now() < session.expires_at:
                    request.user = session.user
                    request.session = session
                else:
                    session.is_active = False
                    session.save()
            except Session.DoesNotExist:
                pass
