from django.core.mail import EmailMultiAlternatives

# import logging  # D13.4
from django.contrib.auth.decorators import login_required  # D6.4
from django.db.models import Exists, OuterRef  # D6.4


from django.contrib.auth.mixins import LoginRequiredMixin   # D5.6
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect  # D6.4

from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from django.shortcuts import redirect

from .filters import NoteFilter, NoteReplyFilter, NoteCatFilter, MyNoteFilter, ReplyFilter
from .models import Category, Subscription   # D6.4
from .forms import NoteForm, NoteReplyForm, ReplyAcceptForm
from .models import Note, NoteReply
from django.contrib.auth.models import User

# logger = logging.getLogger(__name__)


class NotesList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Note
    ordering = '-time_in'
    template_name = 'notes.html'
    context_object_name = 'notes'
    paginate_by = 4

    # Переопределяем функцию получения списка notes
    def get_queryset(self):
        queryset = super().get_queryset()
        # filter by category on the main page.
        self.filterset = NoteCatFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class MyNotesList(ListView):
    # List of my notes - not needed to give author name; similar to NotesList
    model = Note
    ordering = '-time_in'
    template_name = 'my_page.html'
    context_object_name = 'mynotes'
    paginate_by = 4

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(author=self.request.user)
        self.filterset = MyNoteFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class NoteDetail(DetailView):
    model = Note
    template_name = 'note.html'
    # queryset = Note.objects.all()
    context_object_name = 'note'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        connected_replies = NoteReply.objects.filter(note=self.get_object())
        number_of_replies = connected_replies.count()
        context['replies'] = connected_replies
        context['no_of_replies'] = number_of_replies
        context['reply_form'] = NoteReplyForm
        context['showreplyform'] = self._showform()  # trigger for html code to show form or not
        return context

    def _showform(self):
        not_accepted = NoteReply.objects.filter(note=self.get_object()).filter(accept=False)
        return not_accepted.exists()

    def post(self,request, *args, **kwargs):
        if self.request.method == 'POST':
            reply_form = NoteReplyForm(self.request.POST)
            if reply_form.is_valid():
                content = reply_form.cleaned_data['reply']

            new_reply = NoteReply(reply=content, replier = self.request.user, note=self.get_object())
            new_reply.save()
            # We should send email to the author of note about reply
            pub_date = new_reply.reply_time_in  # date of reply
            text_var = new_reply.reply  # text of reply
            note = new_reply.note  #related note
            subject = f'There is a reply on your note: {note.title}'
            note_author_id = note.author_id
            emails = list(User.objects.filter(pk=note_author_id).values_list('email', flat=True))
            email = emails[0]
            msg_text = (f'{pub_date}  |  {text_var}  |   Ссылка на post: http://127.0.0.1:8000{note.get_absolute_url()}\n')
            msg_html = (
                f'{pub_date}  |  {text_var}  |  <br><a href="http://127.0.0.1:8000{note.get_absolute_url()}"></a>\n')
            msg = EmailMultiAlternatives(subject, msg_text, None, [email])
            msg.attach_alternative(msg_html, "text/html")
            msg.send()

            return redirect(self.request.path_info)


class MyNoteDetail(DetailView):
    model = Note
    template_name = 'mynote.html'
    # queryset = Note.objects.all()
    context_object_name = 'mynote'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        connected_replies = NoteReply.objects.filter(note=self.get_object())
        number_of_replies = connected_replies.count()
        context['replies'] = connected_replies
        context['no_of_replies'] = number_of_replies
        return context


class NoteSearch(ListView):
    model = Note
    ordering = '-time_in'
    template_name = 'note_search.html'
    context_object_name = 'note_search'
    paginate_by = 4

    # Переопределяем функцию получения списка notes
    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = NoteFilter(self.request.GET, queryset)
        if not self.request.GET:
            return queryset.none()
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class NoteCreate(LoginRequiredMixin, CreateView):
    permission_required = ('notes.add_note',)
    raise_exception = True
    form_class = NoteForm
    model = Note
    template_name = 'note_create.html'
    success_url = reverse_lazy('notes')

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

class ReplyDelete(LoginRequiredMixin, DeleteView):
    # permission_required = ('notes.delete_note')
    model = NoteReply
    template_name = 'reply_delete.html'
    success_url = reverse_lazy('myreplies')


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

class MyNoteReplyAccept(LoginRequiredMixin, UpdateView):
    # permission_required = ('notes.change_reply')
    form_class = ReplyAcceptForm
    model = NoteReply
    template_name = "mynote_reply_accept.html"
    context_object_name = 'reply_accept'
    success_url = reverse_lazy('mynotes_replylist')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_reply = self.get_object()
        rel_note = current_reply.note
        context['rel_note'] = rel_note
        return context

    def post(self,request, *args, **kwargs):
        accepted_reply = self.get_object()
        if self.request.method == 'POST':
            reply_form = ReplyAcceptForm(self.request.POST)
            if reply_form.is_valid():
                accept_status = reply_form.cleaned_data['accept']

            # new_reply = NoteReply(reply=content, replier = self.request.user, note=self.get_object())
                if accept_status:
                    accepted_reply.accept = accept_status
                    accepted_reply.save()
                # We should send email to the author of note about reply
                    pub_date = accepted_reply.reply_time_in  # date of reply
                    text_var = accepted_reply.reply  # text of reply
                    note = accepted_reply.note  #related note
                    subject = f'There is an acception of your reply: {accepted_reply.reply}'
                    replier_id = accepted_reply.replier_id
                    emails = list(User.objects.filter(pk=replier_id).values_list('email', flat=True))
                    email = emails[0]
                    msg_text = (f'{pub_date}  |  {text_var}  |   Ссылка на note: http://127.0.0.1:8000{note.get_absolute_url()}\n')
                    msg_html = (
                        f'{pub_date}  |  {text_var}  |  <br><a href="http://127.0.0.1:8000{note.get_absolute_url()}"></a>\n')
                    msg = EmailMultiAlternatives(subject, msg_text, None, [email])
                    msg.attach_alternative(msg_html, "text/html")
                    msg.send()

        return redirect('/my_page/mynotesreplies/')


class MyNotesReplyList(ListView):
    model = NoteReply
    template_name = 'mynotes_replylist.html'
    context_object_name = 'mynotes_replylist'
    queryset = NoteReply.objects.all()
    paginate_by = 4

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(note__author=self.request.user)
        self.filterset = NoteReplyFilter(self.request.GET, queryset)
        return self.filterset.qs


class MyRepliesList(ListView):
    model = NoteReply
    template_name = 'myreplies.html'
    context_object_name = 'myreplies'
    queryset = NoteReply.objects.all()
    paginate_by = 4

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(replier=self.request.user)
        self.filterset = ReplyFilter(self.request.GET, queryset)
        return self.filterset.qs


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

