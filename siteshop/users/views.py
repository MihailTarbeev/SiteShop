from django.http import HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView
from users.mixins import MyPermissionMixin
from siteshop import settings
from .forms import ProfileUserForm, RegisterUserForm, LoginForm
from .models import User, Session
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib import messages


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = "users/register.html"
    extra_context = {"title": "Регистрация"}
    success_url = reverse_lazy("users:login")


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        next_url = request.GET.get('next', '')
        return render(request, 'users/login.html', {'form': form, "next": next_url, "title": "Авторизация"})

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(email=email, is_active=True)
            except User.DoesNotExist:
                return render(request, 'users/login.html', {
                    'form': form,
                    'error': 'Неверный email или пароль',
                    'next': request.POST.get('next', '')
                })

            if user.check_password(password):
                session_key = Session.create_session(user)
                next_url = request.POST.get('next')
                redirect_url = next_url if next_url else '/'
                response = redirect(redirect_url)
                response.set_cookie(
                    'sessionid',
                    session_key,
                    max_age=7*24*60*60,
                    httponly=True,
                    secure=True
                )
                return response

        return render(request, 'users/login.html', {
            'form': form,
            'error': 'Неверный email или пароль'
        })


class LogoutView(MyPermissionMixin, View):
    def get(self, request):
        session_key = request.COOKIES.get('sessionid')
        if session_key:
            try:
                session = Session.objects.get(session_key=session_key)
                session.is_active = False
                session.save()
            except Session.DoesNotExist:
                pass

        response = redirect('/users/login/')
        response.delete_cookie('sessionid')
        return response


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

    def post(self, request):
        user = request.user
        user.soft_delete()
        Session.objects.filter(
            user=user, is_active=True).update(is_active=False)
        response = redirect('home')
        response.delete_cookie('sessionid')
        messages.success(request, 'Ваш аккаунт был успешно удалён.')
        return response
