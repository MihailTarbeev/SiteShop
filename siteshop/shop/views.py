# views.py
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json


def home(request):
    """Простая домашняя страница для тестирования"""
    return render(request, 'shop/index.html', context={"title": "Главная страница"})


# def register(request):
#     if request.method == "POST":
#         form = RegisterUserForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data["password"])
#             user.save()
#             return render(request, 'users/register_done.html')
#     else:
#         form = RegisterUserForm()
#     return render(request, "users/register.html", {"form": form, "title": "Регистрация"})

# def test_auth(request):
#     """Тестовый эндпоинт для проверки авторизации"""
#     if hasattr(request, 'user') and request.user.is_authenticated:
#         user = request.user
#         return JsonResponse({
#             'status': 'authenticated',
#             'message': 'User is authenticated',
#             'user': {
#                 'id': str(user.id),
#                 'email': user.email,
#                 'first_name': user.first_name,
#                 'last_name': user.last_name,
#                 'is_active': user.is_active
#             }
#         })
#     else:
#         return JsonResponse({
#             'status': 'anonymous',
#             'message': 'User is not authenticated'
#         }, status=401)


# @csrf_exempt
# @require_http_methods(["POST"])
# def create_test_user(request):
#     """Создание тестового пользователя для проверки (только для разработки)"""
#     try:
#         data = json.loads(request.body)

#         # Проверяем обязательные поля
#         if 'email' not in data or 'password' not in data:
#             return JsonResponse({'error': 'Email and password are required'}, status=400)

#         # Создаем тестового пользователя
#         user = CustomUser.objects.create(
#             email=data['email'],
#             first_name=data.get('first_name', 'Test'),
#             last_name=data.get('last_name', 'User'),
#             patronymic=data.get('patronymic', ''),
#             is_active=True
#         )

#         # Устанавливаем пароль
#         user.set_password(data['password'])
#         user.save()

#         return JsonResponse({
#             'message': 'Test user created successfully',
#             'user': {
#                 'id': str(user.id),
#                 'email': user.email,
#                 'first_name': user.first_name,
#                 'last_name': user.last_name
#             }
#         }, status=201)

#     except json.JSONDecodeError:
#         return JsonResponse({'error': 'Invalid JSON'}, status=400)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=400)


# def generate_test_token(request):
#     """Генерация тестового токена для существующего пользователя (только для разработки)"""
#     try:
#         email = request.GET.get('email')
#         if not email:
#             return JsonResponse({'error': 'Email parameter is required'}, status=400)

#         user = CustomUser.objects.get(email=email, is_active=True)
#         token = user.generate_jwt_token()

#         return JsonResponse({
#             'token': token,
#             'user_email': user.email,
#             'instructions': 'Use this token in Authorization header: Bearer YOUR_TOKEN'
#         })

#     except CustomUser.DoesNotExist:
#         return JsonResponse({'error': 'User not found'}, status=404)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=400)
