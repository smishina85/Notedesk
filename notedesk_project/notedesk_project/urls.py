"""
URL configuration for notedesk_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

# import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('django.contrib.flatpages.urls')),
    # path('accounts/', include('django.contrib.auth.urls')),
    # path('accounts/', include('accounts.urls')),
    path('accounts/', include("allauth.urls")),
    path('', include('notes.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Теперь нам стали доступны новые пути:
# accounts/login/ [name='login']
# accounts/logout/ [name='logout']
# accounts/password_change/ [name='password_change']
# accounts/password_change/done/ [name='password_change_done']
# accounts/password_reset/ [name='password_reset']
# accounts/password_reset/done/ [name='password_reset_done']
# accounts/reset/// [name='password_reset_confirm']accounts/reset/done/ [name='password_reset_complete']
# С подробностями использования представлений (view),
# связанных с каждым из этих путей, можно ознакомиться в официальной документации.
# https://docs.djangoproject.com/en/4.0/topics/auth/default/#all-authentication-views
