from django.utils.deprecation import MiddlewareMixin
from .models import Session, User
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        session_key = request.COOKIES.get('sessionid')
        request.custom_session = None

        if session_key:
            try:
                custom_session = Session.objects.get(
                    session_key=session_key,
                    is_active=True
                )

                if timezone.now() < custom_session.expires_at:
                    request.custom_session = custom_session
                    request.user = custom_session.user
                else:
                    custom_session.is_active = False
                    custom_session.save()
            except Session.DoesNotExist:
                pass
        else:
            request.user = get_user(request)
