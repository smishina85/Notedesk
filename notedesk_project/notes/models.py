from django.db import models
from django.contrib.auth.models import User

from django.utils.translation import gettext as _
from django.utils.translation import pgettext_lazy  # импортируем «ленивый» геттекст с подсказкой

from django.urls import reverse


class Category(models.Model):
    name_cat = models.CharField(max_length=100, unique=True, help_text=_('category name'))  # добавим переводящийся текст подсказку к полю

    def __str__(self):
        return f"{(self.name_cat.title()).upper()}"

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Note(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    time_in = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    title = models.CharField("Заголовок", max_length=128)
    note = models.TextField("Ваше объявление")
    image = models.ImageField(upload_to='images/', blank=True)
    # note = RichTextUploadingField()
    categ = models.ForeignKey(Category, on_delete=models.CASCADE, null=False, verbose_name="Категория")


    def preview(self):
        if self.note:
            return '{} ...'.format(self.note[:125])

    def __str__(self):
        return f"Дата создания: {self.time_in}\n Автор: {self.author}\n Категория: {self.categ}\n Заголовок: {self.title}"

    # @property
    def get_absolute_url(self):
        return reverse('note', args=[str(self.id)])

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'


class NoteReply(models.Model):
    reply = models.TextField('Ваш отклик')
    reply_time_in = models.DateTimeField(auto_now_add=True)
    accept = models.BooleanField(default=False)  # acception of the reply
    # comm_rating = models.IntegerField(default=0)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    replier = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f": replier: {self.replier} , reply: {self.reply}, accept: {self.accept}, note: {self.note_id}"

    class Meta:
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'

    def get_absolute_url(self):
        return reverse('reply', args=[str(self.note)])


class Subscription(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    category = models.ForeignKey(
        to='Category',
        on_delete=models.CASCADE,
        related_name='category',
        verbose_name=pgettext_lazy('help text for Subscription', 'This is the help text'),
    )

