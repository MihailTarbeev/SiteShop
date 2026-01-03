from django.urls import path
from . import views


urlpatterns = [
    path('', views.PeopleHome.as_view(), name='home'),
    path('category/<slug:cat_slug>/',
         views.ShopCategory.as_view(), name='category'),
    path('item/<slug:item_slug>/', views.ShowItem.as_view(), name='item'),
    path('item/<slug:slug>/edit', views.UpdatePage.as_view(), name='edit_item'),
]
