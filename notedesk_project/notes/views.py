from datetime import datetime, timedelta
from pprint import pprint

from django.views.decorators.csrf import csrf_exempt

import logging  # D13.4
from django.contrib.auth.decorators import login_required  # D6.4
from django.db.models import Exists, OuterRef  # D6.4


from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin   # D5.6
from django.core.cache import cache  # импортируем наш кэш
from django.shortcuts import render, get_object_or_404
# D8.4 Кэширование на низком уровне
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect  # D6.4
# Импортируем класс, который говорит нам о том,
# что в этом представлении мы будем выводить список объектов из БД
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from django.contrib.auth import authenticate

from django.http import HttpResponse  # D7.4
#  импортируем респонс для проверки текста

# from django.utils.translation import gettext as _  # импортируем функцию для перевода D14.3
# from django.utils.translation import activate, get_supported_language_variant
from django.utils import timezone
from django.shortcuts import redirect

import pytz  #  импортируем стандартный модуль для работы с часовыми поясами

from .filters import NoteFilter, NoteReplyFilter
from .models import Category, Subscription   # D6.4
from .forms import NoteForm, NoteReplyForm
from .models import Note, NoteReply, User
from django.contrib.auth.models import User



from django.views import View  # D7.4
# from .tasks import hello, printer  # D7.4

import json
# from rest_framework import permissions
# from rest_framework import viewsets, status
# from rest_framework.response import Response

# from . import serializers
# from .serializers import NoteSerializer, AuthorSerializer

import django_filters
logger = logging.getLogger(__name__)


class NotesList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Note
    # Поле, которое будет использоваться для сортировки объектов
    ordering = '-time_in'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'notes.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'notes'
    paginate_by = 4

    # logger.info('INFO')

    # Переопределяем функцию получения списка notes
    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = NoteFilter(self.request.GET, queryset)

        # Возвращаем из функции отфильтрованный список notes
        return self.filterset.qs

    # Метод get_context_data позволяет нам изменить набор данных,
    # который будет передан в шаблон.
    def get_context_data(self, **kwargs):
        # С помощью super() мы обращаемся к родительским классам
        # и вызываем у них метод get_context_data с теми же аргументами,
        # что и были переданы нам.
        # В ответе мы должны получить словарь.
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        # print(context['filterset'])
        # К словарю добавим текущую дату в ключ 'time_now'.
        # context['time_now'] = datetime.utcnow()
        # print(context)
        return context


class MyNotesList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Note
    # Поле, которое будет использоваться для сортировки объектов
    ordering = '-time_in'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'my_page.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'mynotes'
    # paginate_by = 4

    # logger.info('INFO')

    # Переопределяем функцию получения списка notes
    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = NoteFilter(self.request.GET, queryset)

        # Возвращаем из функции отфильтрованный список notes
        return self.filterset.qs

    # Метод get_context_data позволяет нам изменить набор данных,
    # который будет передан в шаблон.
    def get_context_data(self, **kwargs):
        # С помощью super() мы обращаемся к родительским классам
        # и вызываем у них метод get_context_data с теми же аргументами,
        # что и были переданы нам.
        # В ответе мы должны получить словарь.
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        # print(context['filterset'])
        # К словарю добавим текущую дату в ключ 'time_now'.
        # context['time_now'] = datetime.utcnow()
        # print(context)
        return context


class NoteDetail(DetailView):
    model = Note
    template_name = 'note.html'
    queryset = Note.objects.all()
    context_object_name = 'note'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        connected_replies = NoteReply.objects.filter(note=self.get_object())
        number_of_replies = connected_replies.count()
        context['replies'] = connected_replies
        context['no_of_replies'] = number_of_replies
        context['reply_form'] = NoteReplyForm
        # print(self.object.id)
        # print(context['no_of_replies'])
        # print(context)
        return context

    def post(self,request, *args, **kwargs):
        if self.request.method == 'POST':
            print('---------Reached here')
            reply_form = NoteReplyForm(self.request.POST)
            if reply_form.is_valid():
                content = reply_form.cleaned_data['reply']

            new_reply = NoteReply(reply=content, replier = self.request.user, note=self.get_object())
            new_reply.save()
            return redirect(self.request.path_info)


class MyNoteDetail(DetailView):
    model = Note
    template_name = 'mynote.html'
    queryset = Note.objects.all()
    context_object_name = 'mynote'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        connected_replies = NoteReply.objects.filter(note=self.get_object())
        number_of_replies = connected_replies.count()
        context['replies'] = connected_replies
        context['no_of_replies'] = number_of_replies
        print(self.object.id)
        print(context['no_of_replies'])
        print(context)
        return context

    # def post(self, request, *args, **kwargs):
    #     if self.request.method == 'POST':
    #         print('---------Reached here')
    #         reply_form = NoteReplyForm(self.request.POST)
    #         if reply_form.is_valid():
    #             content = reply_form.cleaned_data['reply']
    #
    #         new_reply = NoteReply(reply=content, replier=self.request.user, note=self.get_object())
    #         new_reply.save()
    #         return redirect(self.request.path_info)



class NoteSearch(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Note
    # Поле, которое будет использоваться для сортировки объектов
    ordering = '-time_in'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'note_search.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'note_search'
    paginate_by = 8

    # Переопределяем функцию получения списка note
    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = NoteFilter(self.request.GET, queryset)

        if not self.request.GET:
            return queryset.none()

        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    # Метод get_context_data позволяет нам изменить набор данных,
    # который будет передан в шаблон.
    def get_context_data(self, **kwargs):
        # С помощью super() мы обращаемся к родительским классам
        # и вызываем у них метод get_context_data с теми же аргументами,
        # что и были переданы нам.
        # В ответе мы должны получить словарь.
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        # К словарю добавим текущую дату в ключ 'time_now'.
        #   context['time_now'] = datetime.utcnow()
        return context


class NoteCreate(LoginRequiredMixin, CreateView):
    permission_required = ('notes.add_note',)
    raise_exception = True
    form_class = NoteForm
    model = Note
    template_name = 'note_create.html'

    def image_upload_view(request):
        """Process images uploaded by users"""
        if request.method == 'POST':
            form = NoteForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                # Get the current instance object to display in the template
                img_obj = form.instance
                return render(request, 'note_create.html', {'form': form, 'img_obj': img_obj})
        else:
            form = NoteForm()
        return render(request, 'note_create.html', {'form': form})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)



class NoteDelete(LoginRequiredMixin, DeleteView):
    permission_required = ('notes.delete_note')
    model = Note
    template_name = 'note_delete.html'
    success_url = reverse_lazy('notes')


class NoteUpdate(LoginRequiredMixin, UpdateView):
    permission_required = ('notes.change_note')
    form_class = NoteForm
    model = Note
    template_name = "note_edit.html"

    def image_upload_view(request):
        """Process images uploaded by users"""
        if request.method == 'POST':
            form = NoteForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                # Get the current instance object to display in the template
                img_obj = form.instance
                return render(request, 'note_create.html', {'form': form, 'img_obj': img_obj})
        else:
            form = NoteForm()
        return render(request, 'note_edit.html', {'form': form})

class NoteReplyDetail(DetailView):
    model = NoteReply
    template_name = 'notereply.html'
    queryset = NoteReply.objects.all()
    context_object_name = 'notereply'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class NoteReplyList(ListView):
    model = NoteReply
    template_name = 'reply_list.html'
    context_object_name = 'reply_list'
    queryset = NoteReply.objects.all()

    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = NoteReplyFilter(self.request.GET, queryset)

        # Возвращаем из функции отфильтрованный список notes
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        # С помощью super() мы обращаемся к родительским классам
        # и вызываем у них метод get_context_data с теми же аргументами,
        # что и были переданы нам.
        # В ответе мы должны получить словарь.
        context = super().get_context_data(**kwargs)
        context['acception'] = self.filterset
        # К словарю добавим текущую дату в ключ 'time_now'.
        # context['time_now'] = datetime.utcnow()
        print(context)
        return context

# D6.4

@login_required   # Его могут использовать только зарегистрированные пользователи
@csrf_protect   # у нас будет автоматически проверяться CSRF-токен в получаемых формах
def subscriptions(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Subscription.objects.create(user=request.user,
                                        category=category)
        elif action == 'unsubscribe':
            Subscription.objects.filter(user=request.user,
                                        category=category,
                                        ).delete()
    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(
            Subscription.objects.filter(
                user=request.user,
                category=OuterRef('pk'),
            )
        )
    ).order_by('name_cat')
    return render(
        request,
        'subscriptions.html',
        {'categories': categories_with_subscriptions},
    )

