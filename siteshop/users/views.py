from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.views.generic import CreateView
from .forms import RegisterUserForm, LoginForm
from .models import User, Session
from datetime import datetime
import json


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = "users/register.html"
    extra_context = {"title": "Регистрация"}
    success_url = reverse_lazy("users:register_done")


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'users/login.html', {'form': form})

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
                    'error': 'Неверный email или пароль'
                })

            if user.check_password(password):
                # Создаем сессию
                session_key = Session.create_session(user)

                # Устанавливаем куки
                response = redirect('/')
                response.set_cookie(
                    'sessionid',
                    session_key,
                    max_age=7*24*60*60,  # 7 дней
                    httponly=True,
                    secure=False  # True в production с HTTPS
                )
                return response

        return render(request, 'users/login.html', {
            'form': form,
            'error': 'Неверный email или пароль'
        })


class LogoutView(View):
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
