from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    # path('test-auth/', views.test_auth, name='test_auth'),
    # path('create-test-user/', views.create_test_user, name='create_test_user'),
    # path('generate-token/', views.generate_test_token, name='generate_token'),
]
