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

import HuntLototron.views.home
import HuntLototron.views.match_export
import HuntLototron.views.profile
import HuntLototron.views.profile_settings
import HuntLototron.views.registration

# app_name = 'core'

urlpatterns = [
    path("", HuntLototron.views.home.home, name="home"),
    path("admin/", admin.site.urls),
    path("roulette/", include("roulette.urls")),
    path("stats/", include("stats.urls")),
    path(
        "accounts/profile",
        HuntLototron.views.profile.ProfilePage.as_view(),
        name="profile",
    ),
    path(
        "accounts/profile/edit",
        HuntLototron.views.profile_settings.ProfileSettings.as_view(),
        name="profile_settings",
    ),
    path("accounts/", include("django.contrib.auth.urls")),
    path(
        "accounts/register",
        HuntLototron.views.registration.RegistrationPage.as_view(),
        name="register",
    ),
    path(
        "accounts/profile/edit/delete/<str:hash_key>",
        HuntLototron.views.profile.delete_hash,
        name="delete_hash",
    ),
    path(
        "accounts/profile/csv",
        HuntLototron.views.match_export.export_Matches,
        name="export_csv",
    ),
]
