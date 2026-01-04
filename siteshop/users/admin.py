from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Role, BusinessElement, AccessRoleRule, User, Session
from django.utils.translation import gettext_lazy as _


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    list_display_links = ('id', 'name')
    ordering = ("id",)


@admin.register(BusinessElement)
class BusinessElementAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    list_display_links = ('id', 'name')
    ordering = ("id",)


@admin.register(AccessRoleRule)
class AccessRoleRuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'element',
                    'read_permission', "read_all_permission", 'create_permission',
                    "update_permission", "update_all_permission",
                    "delete_permission", "delete_all_permission")
    list_display_links = ('id',)
    ordering = ('role', "element")


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key_short',
                    'created_at', 'expires_at', 'is_active', 'is_valid')
    list_display_links = ('id', 'user')
    readonly_fields = ('id', 'session_key', 'created_at', 'expires_at', 'user')
    ordering = ("-created_at",)

    @admin.display(description="Ключ сессии")
    def session_key_short(self, obj):
        return f"{obj.session_key[:20]}..." if obj.session_key else ""

    @admin.display(description="Валидна", boolean=True)
    def is_valid(self, obj):
        return obj.is_valid()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'patronymic',
        'role', 'is_active', 'is_staff', 'is_superuser', 'date_joined'
    )
    list_display_links = ('username', 'email')
    ordering = ('-date_joined', 'email')
    readonly_fields = ('date_joined', 'last_login', 'username')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('role')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
         'fields': ('first_name', 'last_name', 'patronymic', 'photo')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff',
         'is_superuser', 'role', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'patronymic', 'role', 'password1', 'password2'),
        }),
    )

    @admin.display(description="Роль")
    def role_name(self, obj):
        return obj.role.name if obj.role else '-'


# admin.site.register(User, UserAdmin)
