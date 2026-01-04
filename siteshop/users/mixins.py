from django.core.exceptions import PermissionDenied
from django.http import HttpResponse


class MyPermissionMixin:
    permission_required = None
    check_ownership = False
    ownership_field = "owner"

    def dispatch(self, request, *args, **kwargs):
        # 1. Проверяем базовое разрешение
        if not request.user.is_authenticated:
            return HttpResponse("<h1>Ошибка 401. Требуется авторизация</h1>", status=401)

        if self.permission_required:
            element_name, field_name = self.permission_required.split('.')

            if not request.user.has_permission_field(element_name, field_name):
                raise PermissionDenied(
                    f"У вас нет разрешения '{field_name}' для объекта '{element_name}'"
                )

        # 2. Для View с объектами проверяем владение (если нужно)
        if self.check_ownership:
            # Получаем объект (для UpdateView, DeleteView, DetailView)
            obj = self.get_object_from_view(request, *args, **kwargs)
            if obj:
                self.check_ownership_permission(request.user, obj)

        return super().dispatch(request, *args, **kwargs)

    def get_object_from_view(self, request, *args, **kwargs):
        """
        Пытается получить объект из View
        Работает для UpdateView, DeleteView, DetailView
        """
        # Если View имеет метод get_object, используем его
        if hasattr(self, 'get_object'):
            try:
                return self.get_object()
            except:
                pass

        # Альтернативный способ для View с pk/slug в URL
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
        """
        Проверяет разрешение с учетом владения
        Для update_permission: проверяет update_all_permission или (владелец + update_permission)
        """
        element_name, field_name = self.permission_required.split('.')

        # Определяем базовое действие (update, delete, read)
        base_action = self.extract_base_action(field_name)

        # Определяем поле для проверки "всех"
        all_permission_field = f"{base_action}_all_permission"

        # Проверяем право на все объекты
        if user.has_permission_field(element_name, all_permission_field):
            return True

        # Проверяем владение
        is_owner = self.is_owner(user, obj)

        # Если владелец и имеет соответствующее разрешение
        if is_owner and user.has_permission_field(element_name, field_name):
            return True

        # Если дошли сюда - нет прав
        raise PermissionDenied(
            f"У вас нет прав для выполнения действия '{base_action}' над этим объектом. "
            f"Вы должны быть владельцем или иметь право '{all_permission_field}'."
        )

    def extract_base_action(self, field_name):
        """Извлекает базовое действие из имени поля"""
        if field_name.endswith('_all_permission'):
            return field_name[:-15]  # Убираем "_all_permission"
        elif field_name.endswith('_permission'):
            return field_name[:-11]  # Убираем "_permission"
        return field_name

    def is_owner(self, user, obj):
        """Проверяет, является ли пользователь владельцем объекта"""
        if not obj:
            return False

        # Проверяем основное поле владения
        if hasattr(obj, self.ownership_field):
            return getattr(obj, self.ownership_field) == user

        # Дополнительные проверки
        owner_fields = ['owner', 'created_by', 'user', 'author', 'creator']
        for field in owner_fields:
            if hasattr(obj, field):
                if getattr(obj, field) == user:
                    return True

        return False
