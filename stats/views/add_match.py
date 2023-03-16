from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from HuntLototron.auxilary import AuxClass
from stats.forms import MatchAddForm


class AddMatch(View):
    def get(self, request):
        user = AuxClass.credentials_to_dict(request)

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
        user = AuxClass.credentials_to_dict(request)
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
