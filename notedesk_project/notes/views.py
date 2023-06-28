from datetime import datetime, timedelta
from pprint import pprint

from django.views.decorators.csrf import csrf_exempt

import logging  # D13.4
from django.contrib.auth.decorators import login_required  # D6.4
from django.db.models import Exists, OuterRef  # D6.4


from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin   # D5.6
from django.core.cache import cache  # импортируем наш кэш
from django.shortcuts import render
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

from .filters import NoteFilter
from .models import Category, Subscription   # D6.4
from .forms import NoteForm
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

# class PostViewset(viewsets.ModelViewSet):
#     queryset = Post.objects.all()
#     serializer_class = serializers.PostSerializer
#     # permission_classes = [IsAuthenticated]
#
# class AuthorViewset(viewsets.ModelViewSet):
#     queryset = Author.objects.all()
#     serializer_class = serializers.AuthorSerializer


# class IndexView(View):
#     def get(self, request):
#
#         current_time = timezone.now()
#
#         #  Translators: This message appears on the home page only
#         # string = _('Hello world')
#
#         models = Category.objects.all()
#         # return HttpResponse(string)
#
#         context = {
#             # 'string': string
#             'models': models,
#             # 'current_time': timezone.now(),
#             'current_time': current_time,
#             'timezones': pytz.common_timezones,
#             #  добавляем в контекст все доступные часовые пояса
#         }
#
#         return HttpResponse(render(request, 'index.html', context))
#
#     #  по пост-запросу будем добавлять в сессию часовой пояс, который и будет обрабатываться написанным нами ранее middleware
#
#     def post(self, request):
#         request.session['django_timezone'] = request.POST['timezone']
#         # return redirect('/')
#         return redirect(request.META.get('HTTP_REFERER'))

# class PostruView(View):
#     def get(self, request):
#         #  Translators: This message appears on the home page only
#         # string = _('Hello world')
#         models = Post.objects.all()
#         # return HttpResponse(string)
#
#         context = {
#             # 'string': string
#             'models': models,
#         }
#
#         return HttpResponse(render(request, 'post.html', context))

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
    paginate_by = 8

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
        # К словарю добавим текущую дату в ключ 'time_now'.
        # context['time_now'] = datetime.utcnow()
        return context


class NoteDetail(DetailView):
    model = Note
    template_name = 'note.html'
    queryset = Note.objects.all()
    context_object_name = 'note'

    # def get_object(self, *args, **kwargs):  # переопределяем метод получения объекта, как ни странно
    #     obj = cache.get(f'post-{self.kwargs["pk"]}', None)  # кэш очень похож на словарь, и метод get действует так же.
    #     # Он забирает значение по ключу, если его нет, то забирает None.
    #
    #     # если объекта нет в кэше, то получаем его и записываем в кэш
    #     if not obj:
    #         obj = super().get_object(queryset=self.queryset)
    #     cache.set(f'post-{self.kwargs["pk"]}', obj)
    #
    #     return obj


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
    paginate_by = 4

    # Переопределяем функцию получения списка товаров
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


class NoteCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('notes.add_note',)
    raise_exception = True
    form_class = NoteForm
    model = Note
    template_name = 'note_create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)



class NoteDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('notes.delete_note')
    model = Note
    template_name = 'note_delete.html'
    success_url = reverse_lazy('notes')


class NoteUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('notes.change_note')
    form_class = NoteForm
    model = Note
    template_name = "note_edit.html"


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
# В представлении мы можем принять как GET, так и POST-запросы:
# GET — будут выполняться, когда пользователь просто открывает страницу подписок;
# POST — когда пользователь нажмёт кнопку подписки или отписки от категории.
# Далее по коду мы делаем непростой запрос в базу данных. Мы соберём все категории товаров с сортировкой по алфавиту и
# добавим специальное поле, которое покажет, подписан сейчас пользователь на данную категорию или нет.

# class IndexView(View):
#     def get(self, request):
#         #printer.delay(10)
#         #printer.apply_async([10], countdown = 5)  # apply_async
#         printer.apply_async([10], eta = datetime.now() + timedelta(seconds=5))
#         hello.delay()
#         return HttpResponse('Hello!')

# Здесь мы использовали класс-представление.
# В методе get() мы написали действия, которые хотим выполнить при вызове этого
# представления — выполнить задачу hello (метод delay() обсудим чуть позже) и вернуть только 'Hello!' в браузер.
# Запустите Django и перейдите на страницу http://127.0.0.1/.

def get_note(_, pk):
    note = Note.objects.get(pk=pk)
    return HttpResponse(content=note, status=200)

def get_notes(_):
    notes = Note.objects.all()
    return HttpResponse(content=notes, status=200)

@csrf_exempt
def create_note(request):
    # permission_classes = [permissions.NotAuthenticated]
    body = json.loads(request.body.decode('utf-8'))
    note = Note.objects.create(
        title=body['title'],
        # charact=body['charact'],
        note=body['text'],
    )
    note.author = 1
    return HttpResponse(content=note, status=201)


def delete_note(_, pk):
    Note.objects.get(pk=pk).delete()
    return HttpResponse(status=204)

def edit_note(request, pk):
    body = json.loads(request.body.decode('utf-8'))
    note = Note.objects.get(pk=pk)
    for attr, value in body.items():
        setattr(note, attr, value)
    note.save()
    data = {"title":note.title, "note": note.note}
    return HttpResponse(content=data, status=200)



#     # def list(self, request, format=None):
#     #     return Response([])
#
#     # def destroy(self, request, pk, format=None):
#     #     instance = self.get_object()
#     #     instance.is_active = False
#     #     instance.save()
#     #     return Response(status=status.HTTP_204_NO_CONTENT)
#
#     def schools(request):
#         if request.method == 'GET':
#             return HttpResponse(json.dumps([
#                 {
#                     "id": school.id,
#                     "address": school.address,
#                     "name": school.name
#                 } for school in School.objects.all()
#             ]))
#         if request.method == 'POST':
#             # Нужно извлечь параметы из тела запроса
#             json_params = json.loads(request.body)
#
#             school = School.objects.create(
#                 name=json_params['name'],
#                 address=json_params['address']
#             )
#             return HttpResponse(json.dumps({
#                 "id": school.id,
#                 "name": school.name,
#                 "school": school.name
#             }))
#
#     def school_id(request, school_id):
#         school = School.objects.get(id=school_id)
#         if request.method == 'GET':
#             return HttpResponse(json.dumps(
#                 {
#                     "id": school.id,
#                     "address": school.address,
#                     "name": school.name
#                 }))
#         json_params = json.loads(request.body)
#         if request.method == 'PUT':
#             school.address = json_params['address']
#             school.name = json_params['name']
#             school.save()
#             return HttpResponse(json.dumps({
#                 "id": school.id,
#                 "name": school.name,
#                 "school": school.name
#             }))
#         if request.method == 'PATCH':
#             school.address = json_params.get('address', school.address)
#             school.name = json_params.get('name', school.name)
#             school.save()
#             return HttpResponse(json.dumps({
#                 "id": school.id,
#                 "name": school.name,
#                 "school": school.name
#             }))
#         if request.method == 'DELETE':
#             school.delete();
#             return HttpResponse(json.dumps({}))
#
# class SClassViewset(viewsets.ModelViewSet):
#     queryset = SClass.objects.all()
#     serializer_class = SClassSerializer
#     permission_classes = []
#     filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
#     filterset_fields = ["grade", "school_id"]
#
# class StudentViewset(viewsets.ModelViewSet):
#     queryset = Student.objects.all()
#     serializer_class = StudentSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         queryset = Student.objects.all()
#         school_id = self.request.query_params.get('school_id', None)
#         sclass_id = self.request.query_params.get('sclass_id', None)
#         if school_id is not None:
#             queryset = queryset.filter(sclass__school_id=school_id)
#         if sclass_id is not None:
#             queryset = queryset.filter(sclass_id=sclass_id)
#         return queryset
#

