from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from .models import Item


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


class ShowItem(DetailView):
    model = Item
    template_name = 'shop/item.html'
    slug_url_kwarg = "item_slug"
    context_object_name = "item"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context["item"].name
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(Item, slug=self.kwargs[self.slug_url_kwarg])
