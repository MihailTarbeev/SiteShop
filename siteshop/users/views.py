from django.db.models.fields import json
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView
from users.serializers import AccessRoleRuleSerializer
from users.mixins import MyPermissionMixin
from siteshop import settings
from .forms import ProfileUserForm, RegisterUserForm, LoginForm
from .models import User, AccessRoleRule
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.forms.models import model_to_dict
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from .utils import jwt_manager


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = "users/register.html"
    extra_context = {"title": "Регистрация"}
    success_url = reverse_lazy("users:login")


class ProfileUser(MyPermissionMixin, UpdateView):
    permission_required = "Users.update_permission"
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = "users/profile.html"
    extra_context = {"title": "Профиль пользователя",
                     "default_user_image": settings.DEFAULT_USER_IMAGE,
                     "default_item_image": settings.DEFAULT_ITEM_IMAGE
                     }

    def get_success_url(self):
        return reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user


class DeleteUser(MyPermissionMixin, View):
    permission_required = "Users.delete_permission"

    def get(self, request):
        return render(request, 'users/delete_confirm.html', {
            'title': 'Удаление аккаунта'
        })

    # def post(self, request):
    #     user = request.user
    #     user.soft_delete()
    #     Session.objects.filter(
    #         user=user, is_active=True).update(is_active=False)
    #     response = redirect('home')
    #     response.delete_cookie('sessionid')
    #     messages.success(request, 'Ваш аккаунт был успешно удалён.')
    #     return response


class ListRulesAPI(generics.ListAPIView):
    queryset = AccessRoleRule.objects.all()
    serializer_class = AccessRoleRuleSerializer
    permission_classes = [IsAdminUser]


class UpdateRuleAPI(generics.RetrieveUpdateAPIView):
    queryset = AccessRoleRule.objects.all()
    serializer_class = AccessRoleRuleSerializer
    permission_classes = [IsAdminUser]


class AboutApi(View):
    def get(self, request):
        return render(request, 'users/about_api.html', {"title": "Про API"})


class LoginView(View):
    """LoginView с автоматическим сохранением токенов в куки"""

    def get(self, request):
        # Если уже аутентифицирован, перенаправляем на главную
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')

        form = LoginForm()
        return render(request, 'users/login.html', {
            'form': form,
            "title": "Авторизация"
        })

    def post(self, request):
        # Обработка HTML формы
        form = LoginForm(request.POST)
        if not form.is_valid():
            return render(request, 'users/login.html', {
                'form': form,
                'error': 'Неверные данные'
            })

        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        # Ищем пользователя
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return render(request, 'users/login.html', {
                'form': LoginForm(),
                'error': 'Неверный email или пароль'
            })

        # Проверяем пароль
        if not user.check_password(password):
            return render(request, 'users/login.html', {
                'form': LoginForm(),
                'error': 'Неверный email или пароль'
            })

        # Успешная авторизация - редирект с установкой кук
        response = HttpResponseRedirect('/')
        response = jwt_manager.create_tokens_for_response(user, response)
        return response


class LogoutView(View):
    """Logout с очисткой кук"""

    def get(self, request):
        response = HttpResponseRedirect('/users/login/')

        # Очищаем куки
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        # Отзываем refresh token из БД если есть
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            from .models import RefreshToken
            try:
                rt = RefreshToken.objects.get(token=refresh_token)
                rt.is_active = False
                rt.save()
            except RefreshToken.DoesNotExist:
                pass

        return response
