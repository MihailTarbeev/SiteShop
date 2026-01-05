from django.core.exceptions import PermissionDenied
from django.http import HttpResponse


class MyPermissionMixin:
    permission_required = None
    check_ownership = False
    ownership_field = "owner"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponse("<h1>Ошибка 401. Требуется авторизация</h1>", status=401)

        if self.permission_required:
            element_name, field_name = self.permission_required.split('.')

            if not request.user.has_permission_field(element_name, field_name):
                raise PermissionDenied(
                    f"У вас нет разрешения '{field_name}' для объекта '{element_name}'"
                )

        if self.check_ownership:
            obj = self.get_object_from_view(request, *args, **kwargs)
            if obj:
                self.check_ownership_permission(request.user, obj)

        return super().dispatch(request, *args, **kwargs)

    def get_object_from_view(self, request, *args, **kwargs):
        """Пытается получить объект из View"""
        if hasattr(self, 'get_object'):
            try:
                return self.get_object()
            except:
                pass

        model = getattr(self, 'model', None)
        if model:
            try:
                if 'pk' in kwargs:
                    return model.objects.get(pk=kwargs['pk'])
                elif 'slug' in kwargs:
                    return model.objects.get(slug=kwargs['slug'])
            except:
                pass

        return None

    def check_ownership_permission(self, user, obj):
        """Проверяет разрешение с учетом владения"""
        element_name, field_name = self.permission_required.split('.')

        base_action = self.extract_base_action(field_name)

        all_permission_field = f"{base_action}_all_permission"

        if user.has_permission_field(element_name, all_permission_field):
            return True

        if self.is_owner(user, obj):
            return True

        raise PermissionDenied(
            f"У вас нет прав для выполнения действия '{base_action}' над этим объектом. "
            f"Вы должны быть владельцем или иметь право '{all_permission_field}'."
        )

    def extract_base_action(self, field_name):
        """Извлекает действие из имени поля"""
        if field_name.endswith('_all_permission'):
            return field_name[:-15]
        elif field_name.endswith('_permission'):
            return field_name[:-11]
        return field_name

    def is_owner(self, user, obj):
        """Проверяет, является ли пользователь владельцем объекта"""
        if not obj:
            return False

        if hasattr(obj, self.ownership_field):
            return getattr(obj, self.ownership_field) == user

        return False
