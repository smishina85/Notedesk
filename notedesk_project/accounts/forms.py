# from django.contrib.auth.forms import UserCreationForm
from allauth.account.forms import SignupForm  # D5.5

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
# from django.core.mail import send_mail
from django.core.mail import mail_admins
from django.core.mail import mail_managers


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=128, label="Имя", required=False)

    class Meta:
        model = User
        fields = ("first_name")

    def save(self, request):
        user = super().save(request)
        common_users = Group.objects.get(name="Common users")
        user.groups.add(common_users)
        if user.first_name:
            name = user.first_name
        else:
            name = user.username

        # send_mail(
        subject = f'Добро пожаловать на наш портал объявлений!'
        # message=f'{user.username}, Вы успешно зарегестрировались!',
        text = f"{name}, Вы успешно зарегестрировались на сайте! Ваш логин - это Ваш электронный адрес: {user.email}"
        # from_email=None, # будет использовано значение DEFAULT_FROM_EMAIL
        # recipient_list=[user.email],
        # )
        # print(name)
        html = (
            f'<b>{name}</b>, Вы успешно зарегестрировались на '
            f'<a href="http://127.0.0.1:8000/"> сайте</a>!'
        )
        msg = EmailMultiAlternatives(
            subject=subject, body=text, from_email=None, to=[user.email]
        )
        msg.attach_alternative(html, "text/html")
        msg.send()

        # mail_managers(
        #     subject=f'Новый Пользователь',
        #     message=f'Информируем, что Пользователь {user.username} зарегестрирован на нашем сайте '
        #
        # )
        mail_admins(
            subject=f'Новый Пользователь',
            message=f'Информируем, что Пользователь {user.username} зарегестрирован на нашем сайте '
        )

        return user
# Функция send_mail позволяет отправить письмо указанному получателю в recipient_list.
# В поле subject мы передаём тему письма, а в message — текстовое сообщение.


# class SignUpForm(UserCreationForm):
#     email = forms.EmailField(label="Email")
#     first_name = forms.CharField(label="Имя")
#     last_name = forms.CharField(label="Фамилия")
#
#     class Meta:
#         model = User
#         fields = (
#             "username",
#             "first_name",
#             "last_name",
#             "email",
#             "password1",
#             "password2",
#         )
