from django.contrib import admin

from .models import Category, Note, NoteReply, Subscription


class NoteAdmin(admin.ModelAdmin):
    list_display = ('time_in', 'author', 'title', 'categ', 'note')
    list_filter = ('time_in', 'author')
    search_fields = ('time_in', 'author', 'title')

class NoteReplyAdmin(admin.ModelAdmin):
    list_display = ('reply_time_in', 'replier', 'reply', 'accept')
    list_filter = ('reply_time_in', 'replier', 'accept')
    search_fields = ('reply_time_in', 'replier')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'category')
    list_filter = ('user', 'category')

admin.site.register(Category)
admin.site.register(Note, NoteAdmin)
admin.site.register(NoteReply, NoteReplyAdmin)
admin.site.register(Subscription, SubscriptionAdmin)

# Register your models here.
