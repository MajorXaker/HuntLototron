from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.shortcuts import render
from django.views import View

from stats import models as m
from stats.models import Match
from stats.utils.get_credentials import UserCredsOrganised


class MatchesTable(View):
    def get(self, request: WSGIRequest):
        user = UserCredsOrganised.from_request(request)

        if request.user.is_staff:
            matches_for_view = m.Match.objects.all()
        elif not request.user.pk:
            matches_for_view = self.get_available_matches()
        else:
            matches_for_view = self.get_players_matches(user=user, request=request)

        return render(
            request,
            "stats_list.html",
            {
                "matches": matches_for_view,
                "user": user,
            },
        )

    @staticmethod
    def get_available_matches() -> list[Match]:
        available_matches = [
            match for match in m.Match.objects.all() if match.display_allowed()
        ]
        [match.set_encoding() for match in available_matches]
        return available_matches

    def get_players_matches(
        self, user: UserCredsOrganised, request: WSGIRequest
    ) -> list[Match]:
        if user.has_aka:
            look_for_user = m.Player.objects.get(also_known_as=user.playername)
        else:
            look_for_user = User.objects.get(username=user.username).username_of_player

        player_matches = m.Match.objects.filter(
            Q(player_1=look_for_user)
            | Q(player_2=look_for_user)
            | Q(player_3=look_for_user)
        )

        others_matches = []
        if not request.user.username_of_player.show_only_my_matches:
            others_matches = self.get_available_matches()

        result_as_list = sorted(
            {*player_matches, *others_matches}, key=lambda match: match.id
        )

        return result_as_list
