from django.contrib import admin

from .models import Category, Note, NoteReply, Subscription


# импортируем модель амдинки (вспоминаем модуль про переопределение стандартных админ-инструментов)

# Register your models here.

# Регистрируем модели для перевода в админке

# class CategoryAdmin(TranslationAdmin):
#     model = Category
#
# class PostruAdmin(TranslationAdmin):
#     model = Post


# def nullfy_rating(modeladmin, request, queryset):
#     queryset.update(rating=0)
# nullfy_rating.short_description = 'Nullfy the rating'

class NoteAdmin(admin.ModelAdmin):
    list_display = ('time_in', 'author', 'title', 'categ', 'note')
    list_filter = ('time_in', 'author')
    search_fields = ('time_in', 'author', 'title')

class NoteReplyAdmin(admin.ModelAdmin):
    list_display = ('reply_time_in', 'replier', 'reply', 'accept')
    list_filter = ('reply_time_in', 'replier', 'accept')
    search_fields = ('reply_time_in', 'replier')


# class AuthorAdmin(admin.ModelAdmin):
#     list_display = ('fio_author', 'rating')
#     list_filter = ('user__last_name', 'rating')
#     actions = [nullfy_rating]


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'category')
    list_filter = ('user', 'category')

admin.site.register(Category)
admin.site.register(Note, NoteAdmin)
admin.site.register(NoteReply, NoteReplyAdmin)
# admin.site.register(PostCategory)
admin.site.register(Subscription, SubscriptionAdmin)
# admin.site.register(MyModel)

# Register your models here.
