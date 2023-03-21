from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from HuntLototron.auxilary import AuxClass
from stats import models as m
from stats.forms import MatchEditForm


class EditMatch(LoginRequiredMixin, View):
    def get(self, request, match_id):
        user = AuxClass.credentials_to_dict(request)

        match_on_table = m.Match.objects.get(pk=match_id)
        form = MatchEditForm(instance=match_on_table)
        user["position"] = match_on_table.get_player_slot(user["credentials"])
        if user["position"] is None and request.user.is_staff == False:
            return render(request, "404_or_403_match.html", status=403)

        context = {
            "form": form,
            "user": user,
        }

        output = render(request, "edit_match.html", context)

        return output

    def post(self, request, match_id):
        user = AuxClass.credentials_to_dict(request)
        form = MatchEditForm(
            request.POST,
        )

        match_on_table = m.Match.objects.get(pk=match_id)
        user["position"] = match_on_table.get_player_slot(user["credentials"])

        if form.is_valid():
            print(
                f"In match player 1 m weapon is {match_on_table.player_1_primary_weapon}, its size is {match_on_table.player_1_primary_weapon.size}"
            )

            # print(match_on_table.verify_guns(user["position"])[0])
            form.save()

            return HttpResponseRedirect(reverse("stats:table"))

        context = {"form": form, "user": user}

        output = render(request, "edit_match.html", context)

        return output
