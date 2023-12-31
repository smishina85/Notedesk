from importlib.resources import _

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, Textarea

from .models import Category, Note, NoteReply


class NoteForm(forms.ModelForm):
    title = forms.CharField(label='Заголовок', min_length=4)
    categ = ModelChoiceField(label='Категория', queryset=Category.objects.all())

    class Meta:
        model = Note
        fields = [
            # 'author',
            # 'charact',
            'title',
            'categ',
            'note',
            'image',
        ]
        labels = {'note': _('Ваш Текст'), }
        widgets = {'title': Textarea(attrs={'cols': 128, 'rows': 2}), 'note': Textarea(attrs={'cols': 80, 'row': 10}),
                    'categ': Textarea(attrs={'cols': 50}),
                   }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")

        if title is not None and len(title) < 4:
            raise ValidationError({
                 "title": "Заголовок не может быть менее 4 смволов"
            })
        return cleaned_data

    def clean_title(self):
        title = self.cleaned_data["title"]
        if title[0].islower():
            raise ValidationError("Заголовок должен начинаться с заглавной буквы")
        return title
