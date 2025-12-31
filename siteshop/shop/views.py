from django.http import Http404, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify


menu = [
    {'title': 'О сайте', 'url_name': 'about'},
    {'title': 'Добавить статью', 'url_name': 'add_page'},
    {'title': 'Обратная связь', 'url_name': 'contact'},
    {'title': 'Войти', 'url_name': 'login'},
]

data_db = [
    {'id': 1, "name": 'Михаил', 'content':

     '''
         <p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Donec libero.
      ЭЭЭSuspendisse bibendum. Cras id urna. Morbi tincidunt, orci ac convallis
      aliquam, lectus turpis varius lorem, eu posuere nunc justo tempus leo.
      Donec mattis, purus nec placerat bibendum, dui pede condimentum odio, ac
      blandit ante orci ut diam. Cras fringilla magna. Phasellus suscipit, leo a
      pharetra condimentum, lorem tellus eleifend magna, eget fringilla velit
      magna id neque. Curabitur vel urna. In tristique orci porttitor ipsum.
      Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Donec libero.
      Suspendisse bibendum. Cras id urna. Morbi tincidunt, orci ac convallis
      aliquam, lectus turpis varius lorem, eu posuere nunc justo tempus leo.
    </p>
    <p>
      Aenean consequat porttitor adipiscing. Nam pellentesque justo ut tortor
      congue lobortis. Donec venenatis sagittis fringilla. Etiam nec libero
      magna, et dictum velit. Proin mauris mauris, mattis eu elementum eget,
      commodo in nulla. Mauris posuere venenatis pretium. Maecenas a dui sed
      lorem aliquam dictum. Nunc urna leo, imperdiet eu bibendum ac, pretium ac
      massa. Cum sociis natoque penatibus et magnis dis parturient montes,
      nascetur ridiculus mus. Nulla facilisi. Quisque condimentum luctus
      ullamcorper.
    </p>
     ''', "is_published": True},
    {'id': 2, "name": 'Иван', 'content': '<p>Одногруппник хорошего человека</p>',
        "is_published": True},
    {'id': 3, "name": 'Борис', 'content': 'Неизвестный парень', "is_published": True},
    {'id': 4, "name": 'Инокентий',
        'content': 'Неизвестный парень', "is_published": False},
]


def index(request):
    data = {"title": 'Главная страница',
            "menu": menu,
            "posts": data_db
            }
    return render(request, 'shop/index.html', context=data)


def addpage(request):
    return HttpResponse(f'Добавление статьи')


def contact(request):
    return HttpResponse(f'Обратная связь')


def login(request):
    return HttpResponse(f'Авторизация')


def about(request):
    data = {"title": 'О сайте', 'menu': menu}
    return render(request, 'shop/about.html', context=data)


def show_post(request, post_id):
    return HttpResponse(f'Отображение статьи с id:{post_id}')


def page_not_found_view(request, exception=None):
    return HttpResponseNotFound(f"<h1>Ты не туда зашёл. Выйди!</h1>")
