from django.contrib import admin
from django.urls import path, include
from django.views.decorators.cache import cache_page  # this is a page to be cached

# from rest_framework import routers

# Импортируем созданное нами представление
from .views import NoteCreate, NoteDelete, NoteDetail, NoteSearch, NoteUpdate, NotesList, subscriptions, NoteReplyList, MyNotesList, MyNoteDetail
# D8
# from .views import get_note, get_notes, create_note, delete_note, edit_note

# router = routers.DefaultRouter()
# router.register(r'post', PostViewset)
# router.register(r'author', AuthorViewset)

urlpatterns = [
    # path — означает путь.
    # В данном случае путь ко всем новостям у нас останется пустым,
    # чуть позже станет ясно почему.
    # Т.к. наше объявленное представление является классом,
    # а Django ожидает функцию, нам надо представить этот класс в виде view.
    # Для этого вызываем метод as_view.
    # path('', cache_page(60)(PostsList.as_view()), name='posts'),  # Добавьте кэширование на главную страницу (одну минуту)
    # pk — это первичный ключ новости, который будет выводиться у нас в шаблон
    # int — указывает на то, что принимаются только целочисленные значения
    # path('<int:pk>', cache_page(150)(PostDetail.as_view()), name='post'), #Добавьте кэширование на страницы с новостями (по 5 минут на каждую)
    path('', NotesList.as_view(), name='notes'),
    path('<int:pk>', NoteDetail.as_view(), name='note'),
    path('search/', NoteSearch.as_view(), name='note_search'),
    path('create/', NoteCreate.as_view(), name='note_create'),
    path('<int:pk>/delete/', NoteDelete.as_view(), name='note_delete'),
    path('<int:pk>/edit/', NoteUpdate.as_view(), name='note_edit'),
    path('replies/', NoteReplyList.as_view(), name='reply_list'),
    path('subscriptions/', subscriptions, name='subscriptions'),
    path('my_page/mynote/', MyNoteDetail.as_view(), name='mynote'),
    path('my_page/', MyNotesList.as_view(), name='my_page')
    # path('index/', IndexView.as_view(), name='index'),
    # D15
    # path('note/<int:pk>/', get_note),
    # path('notes/', get_notes),
    # path('create_note/', create_note),
    # path('delete_note/<int:pk>/', delete_note),
    # path('edit_note/<int:pk>/', edit_note),
    # path('api/', include(router.urls), name='api'),
    # path('postru/', PostruView.as_view(), name='postru'),
]
