"""HuntLototron URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from . import views

# app_name = 'core'

urlpatterns = [
    path('', views.home),
    path('admin/', admin.site.urls),
    path('roulette/', include('roulette.urls')),
    path('stats/', include('stats.urls')),
    path('accounts/profile', views.ProfilePage.as_view(), name='profile'),
    path('accounts/profile/edit', views.ProfileSettings.as_view(), name='profile_settings'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register', views.RegistrationPage.as_view(), name='register'),
]

