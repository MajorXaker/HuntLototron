from itertools import chain
from operator import attrgetter

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from HuntLototron.auxilary import AuxClass, MatchesDecoder
from HuntLototron.forms import CSVUploadForm
from stats import models as m


class ProfilePage(LoginRequiredMixin, View):
    login_url = "/accounts/login/"
    redirect_field_name = "redirect_to"

    def get(self, request):
        user = AuxClass.credentials_to_dict(request)

        csv_form = CSVUploadForm()

        additional = {}
        context = {"user": user, "additional": additional, "csv_form": csv_form}

        return render(request, "registration/profile.html", context)

    def post(self, request):
        user = AuxClass.credentials_to_dict(request)
        csv_form = CSVUploadForm(request.POST, request.FILES)
        player = request.user.username

        if csv_form.is_valid():
            print("Form valid")
            filename = request.FILES["file"].name
            file_as_text = open(filename, "r")

            decoder = MatchesDecoder(file_as_text, player)

            decoder.normalise()

            decoder.transfer()

            response = HttpResponse(
                content_type="text/txt",
                headers={"Content-Disposition": 'attachment; filename="log.txt"'},
            )
            for message in decoder.messages:
                response.write(message)
                response.write("\n")
                response.write("----")
                response.write("\n")
            return response

            # with open("log.txt", 'wt') as file:
            #     for message in messages:
            #         file.write(message)

        else:
            print("Form invalid")
            print(csv_form.errors)

        additional = {}
        context = {"user": user, "additional": additional, "csv_form": csv_form}

        return render(request, "registration/profile.html", context)


def delete_hash(request, hash_key):
    hashed_player = m.Player.objects.get(hash_key=hash_key)

    # look if this player participated in any matches
    matches_p1 = m.Match.objects.filter(player_1=hashed_player)
    matches_p2 = m.Match.objects.filter(player_2=hashed_player)
    matches_p3 = m.Match.objects.filter(player_3=hashed_player)

    matches_as_list = sorted(
        chain(matches_p1, matches_p2, matches_p3), key=attrgetter("id")
    )

    if len(matches_as_list) > 0:
        # do smth if mathes are found TBD
        # for example change with unknown player

        unknown_player = User.objects.get(username="UnknownHunter").username
        for match in matches_as_list:
            match.swap_players(hashed_player, unknown_player)
        hashed_player.delete()
        return redirect("profile_settings", permanent=True)
    else:
        # delete this hash if mathes are not found
        hashed_player.delete()
        return redirect("profile_settings", permanent=True)
