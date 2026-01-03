from django.shortcuts import render
from django.views.generic import ListView
from .models import Item


def home(request):
    """Простая домашняя страница для тестирования"""
    return render(request, 'shop/index.html', context={"title": "Главная страница"})


class PeopleHome(ListView):
    model = Item
    template_name = "shop/index.html"
    context_object_name = "items"
    extra_context = {"title": "Главная страница", "category_selected": 0}

    def get_queryset(self):
        return Item.objects.all().select_related("category")


class ShopCategory(ListView):
    template_name = 'shop/index.html'
    context_object_name = "items"
    allow_empty = False

    def get_queryset(self):
        return Item.objects.filter(category__slug=self.kwargs["cat_slug"]).select_related("category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = context["items"][0].category
        context['category_selected'] = category.pk
        context['title'] = "Категория - " + category.name
        return context
