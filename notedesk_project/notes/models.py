from django.core.cache import cache
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from django.utils.translation import gettext as _
from django.utils.translation import pgettext_lazy  # импортируем «ленивый» геттекст с подсказкой


# D8.4
from django.db.models import Sum
from django.urls import reverse


# class Author(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     # rating = models.SmallIntegerField(default=0)
#
#     def __str__(self):
#         return f"{self.user.first_name} {self.user.last_name}"
#
#     @property
#     def fio_author(self):
#         return f"{self.user.first_name} {self.user.last_name}"

    # def update_rating(self):
    #     postRat = self.post_set.all().aggregate(Sum('rating_post'))
    #     pRat = 0
    #     pRat += postRat.get('rating_post__sum')
    #
    #     cRat = 0
    #     cpRat = 0
    #     if self.user.comment_set.all():
    #         commentRat = self.user.comment_set.all().aggregate(Sum('comm_rating'))
    #         cRat += commentRat.get('comm_rating__sum')
    #         commpostRat = Comment.objects.filter(post__in= self.post_set.all()).exclude(user__author__in=[self]).aggregate(Sum('comm_rating'))
    #         cpRat += commpostRat.get('comm_rating__sum')
    #
    #     self.rating = pRat * 3 + cRat + cpRat
    #     self.save()

    # class Meta:
    #     verbose_name = 'Автор'
    #     verbose_name_plural = 'Авторы'


class Category(models.Model):
    name_cat = models.CharField(max_length=100, unique=True, help_text=_('category name'))  # добавим переводящийся текст подсказку к полю

    def __str__(self):
        return f"{(self.name_cat.title()).upper()}"

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


# class MyModel(models.Model):
#     name = models.CharField(max_length=100)
#     kind = models.ForeignKey(
#         Category,
#         on_delete=models.CASCADE,
#         related_name='kinds',
#         verbose_name=pgettext_lazy('help text for MyModel model', 'This is the help text'),
#     )

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

    # def __str__(self):
    #     cat_list = list(((self.post).all()).values('name_cat'))
    #     # if cat_list:
    #     #     print(cat_list[0]['name_cat'])
    #     cat_str = ''
    #     if cat_list:
    #         for i in range(len(cat_list)):
    #             cat_str += cat_list[i]['name_cat'] + ' '
    #     else:
    #         cat_str += 'Assign category'
    #     # print(cat_str)
    #     # print(cat_list)
    #     return f"Date of creation: {self.time_in}\n Author: {self.author.user}\n (Rating: {self.rating_post})\n Title: {self.title} \n( {cat_str})"

    def __str__(self):
        return f"Дата создания: {self.time_in}\n Автор: {self.author}\n Категория: {self.categ}\n Заголовок: {self.title}"

    # @property
    # def cat_adm(self):
    #     cat_list = list(((self.note).all()).values('name_cat'))
    #     cat_str = ''
    #     if cat_list:
    #         for i in range(len(cat_list)):
    #             cat_str += cat_list[i]['name_cat'] + ' '
    #     else:
    #         cat_str += 'Категория не назначена'
    #     return cat_str

    # @property
    def get_absolute_url(self):
        return reverse('note', args=[str(self.id)])

    # D8.4 - кэширование
    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
    #     cache.delete(f'note-{self.pk}')  # затем удаляем его из кэша, чтобы сбросить его

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'


# class NoteCategory(models.Model):
#     note = models.ForeignKey(Note, on_delete=models.CASCADE)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#
#     def __str__(self):
#         return f"{self.note.title}  -  Category: {self.category}"
#
#     class Meta:
#         verbose_name = 'Категория объявления'
#         verbose_name_plural = 'Категории Объявлений'


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

