from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.views import View

from HuntLototron.auxilary import AuxClass
from stats import models as m


class MatchDetails(View):
    def get(self, request: WSGIRequest, match_id: int):
        user = AuxClass.credentials_to_dict(request)
        try:
            match = m.Match.objects.get(pk=match_id)
        except m.Match.DoesNotExist:
            return render(request, "404_or_403_match.html", status=403)

        open_for_browsing = any(
            (
                request.user.is_staff,
                getattr(request.user, "username_of_player", None) in match.players(),
                match.display_allowed(),
            )
        )
        if not open_for_browsing:
            return render(request, "404_or_403_match.html", status=403)

        if getattr(request.user, "username_of_player", "") not in match.players():
            match.set_encoding()

        # additional = {
        #     "player_2_here": match.player_2 is not None,
        #     "player_3_here": match.player_3 is not None,
        # }
        additional = {}

        # temporary placeholder, as bounty for now is only 4 match, not for person
        # additional['player_1_bounty'] =  match.bounty
        # additional['player_2_bounty'] =  match.bounty
        # additional['player_3_bounty'] =  match.bounty

        response = render(
            request,
            "detailed_stats.html",
            {"match": match, "additional": additional, "user": user},
        )

        return response
