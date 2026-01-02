from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from .models import BusinessElement, AccessRoleRule


class MultiPermissionMixin:
    """
    Миксин для проверки нескольких разрешений одновременно
    Формат permissions_required: ["element1.field1", "element2.field2", ...]
    """
    permissions_required = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponse(
                "<h1>Ошибка 401. Требуется авторизация</h1>",
                status=401
            )

        for permission in self.permissions_required:
            if not self.check_permission(request.user, permission):
                element_name, field_name = permission.split('.')
                raise PermissionDenied(
                    f"У вас нет разрешения '{field_name}' "
                    f"для объекта '{element_name}'"
                )

        return super().dispatch(request, *args, **kwargs)

    def check_permission(self, user, permission_string):
        """Проверяет одно конкретное разрешение"""
        try:
            element_name, field_name = permission_string.split('.')
        except ValueError:
            return False

        try:
            element = BusinessElement.objects.get(name=element_name)
            rule = AccessRoleRule.objects.get(role=user.role, element=element)
            return getattr(rule, field_name, False)
        except (BusinessElement.DoesNotExist, AccessRoleRule.DoesNotExist):
            return False
