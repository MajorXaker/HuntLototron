from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from stats.forms import MatchAddForm
from utils.get_credentials import UserCredsOrganised


class AddMatch(LoginRequiredMixin, View):
    login_url = "/accounts/login/"
    redirect_field_name = 'redirect_to'

    def get(self, request):
        user = UserCredsOrganised.from_request(request)

        initial_data = {
            "player_1": request.user.username_of_player,
        }

        form = MatchAddForm(initial=initial_data)

        context = {
            "form": form,
            "user": user,
        }

        output = render(request, "add_match.html", context)

        return output

    def post(self, request):
        user = UserCredsOrganised.from_request(request)
        form = MatchAddForm(request.POST)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse("stats:table"))
        else:
            print("not valid form")
            print(form.errors)

        context = {"form": form, "user": user}

        output = render(request, "add_match.html", context)

        return output
