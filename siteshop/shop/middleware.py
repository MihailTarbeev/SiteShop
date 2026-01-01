from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .models import CustomUser
import re


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request.user = AnonymousUser()

        # Получаем заголовок Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            user = CustomUser.verify_jwt_token(token)
            if user:
                request.user = user

        response = self.get_response(request)

        return response
