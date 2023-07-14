from django.urls import path

# Импортируем созданное нами представление
from .views import NoteCreate, NoteDelete, NoteDetail, NoteSearch, NoteUpdate, NotesList, subscriptions, \
    MyNotesList, MyNoteDetail, MyNotesReplyList, ReplyDelete, MyNoteReplyAccept, MyRepliesList


urlpatterns = [
    path('', NotesList.as_view(), name='notes'),
    path('<int:pk>', NoteDetail.as_view(), name='note'),
    path('search/', NoteSearch.as_view(), name='note_search'),
    path('create/', NoteCreate.as_view(), name='note_create'),
    path('<int:pk>/delete/', NoteDelete.as_view(), name='note_delete'),
    path('<int:pk>/edit/', NoteUpdate.as_view(), name='note_edit'),
    path('subscriptions/', subscriptions, name='subscriptions'),
    path('my_page/mynote/<int:pk>', MyNoteDetail.as_view(), name='mynote'),
    path('my_page/mynotesreplies/', MyNotesReplyList.as_view(), name='mynotes_replylist'),
    path('my_page/<int:pk>/delete/', ReplyDelete.as_view(), name='reply_delete'),
    path('my_page/<int:pk>/accept/', MyNoteReplyAccept.as_view(), name='reply_accept'),
    path('my_page/myreplies/', MyRepliesList.as_view(), name='myreplies'),
    path('my_page/', MyNotesList.as_view(), name='my_page'),
]
