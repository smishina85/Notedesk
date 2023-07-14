from django.forms import DateInput

import django_filters
from django_filters import FilterSet

from .models import Note, NoteReply

# Создаем свой набор фильтров для модели Note.
# FilterSet, который мы наследуем,
# должен чем-то напомнить знакомые вам Django дженерики.


class NoteFilter(FilterSet):

    class Meta:

        # В Meta классе мы должны указать Django модель,
        # в которой будем фильтровать записи.
        model = Note
        # В fields мы описываем по каким полям модели
        # будет производиться фильтрация.
        fields = {
                'author': ['exact'],
                'title': ['icontains'],
                'note': ['icontains'],
                'categ': ['exact'],
            }

    date = django_filters.DateTimeFilter(
        field_name='time_in',
        lookup_expr='gt',
        label='Дата',
        widget=DateInput(attrs={'type': 'date'},
                         )
    )

class NoteCatFilter(FilterSet):

    class Meta:

        # В Meta классе мы должны указать Django модель,
        # в которой будем фильтровать записи.
        model = Note
        # В fields мы описываем по каким полям модели
        # будет производиться фильтрация.
        fields = {
                # 'author': ['exact'],
                # 'title': ['icontains'],
                # 'note': ['exact'],
                'categ': ['exact'],
            }


class MyNoteFilter(FilterSet):

    class Meta:

        # В Meta классе мы должны указать Django модель,
        # в которой будем фильтровать записи.
        model = Note
        # В fields мы описываем по каким полям модели
        # будет производиться фильтрация.
        fields = {
                # 'author': ['exact'],
                'title': ['icontains'],
                # 'note': ['exact'],
                'categ': ['exact'],
            }

    date = django_filters.DateTimeFilter(
        field_name='time_in',
        lookup_expr='gt',
        label='Дата',
        widget=DateInput(attrs={'type': 'date'},
                         )
    )

class NoteReplyFilter(FilterSet):
    class Meta:

        # В Meta классе мы должны указать Django модель,
        # в которой будем фильтровать записи.
        model = NoteReply
        # В fields мы описываем по каким полям модели
        # будет производиться фильтрация.
        fields = {
                'accept': ['exact'],
            }

class ReplyFilter(FilterSet):
    class Meta:

        # В Meta классе мы должны указать Django модель,
        # в которой будем фильтровать записи.
        model = NoteReply
        # В fields мы описываем по каким полям модели
        # будет производиться фильтрация.
        fields = {
                'reply': ['icontains'],
                'note': ['exact'],
                'accept': ['exact'],
            }


