from django.shortcuts import render

from HuntLototron.auxilary import AuxClass
from stats import models as m


def show_match_detail(request, match_id):
    try:
        match = m.Match.objects.get(pk=match_id)
        user = AuxClass.credentials_to_dict(request)

        open_for_browsing = (
            request.user.is_staff,
            request.user.username_of_player in match.players(is_class=True),
            match.display_allowed(),
        )  # one TRUE result lets us to see the match

        if not request.user.username_of_player in match.players(is_class=True):
            match.set_encoding()

        additional = {}
        additional["player_2_here"] = (
            False if str(type(match.player_2)) == "<class 'NoneType'>" else True
        )
        additional["player_3_here"] = (
            False if str(type(match.player_3)) == "<class 'NoneType'>" else True
        )

        # temporary placeholder, as bounty for now is only 4 match, not for person
        # additional['player_1_bounty'] =  match.bounty
        # additional['player_2_bounty'] =  match.bounty
        # additional['player_3_bounty'] =  match.bounty

        if True in open_for_browsing:
            response = render(
                request,
                "detailed_stats.html",
                {"match": match, "additional": additional, "user": user},
            )
        else:
            response = render(request, "404_or_403_match.html", status=403)

        return response
    except m.Match.DoesNotExist:
        return render(request, "404_or_403_match.html", status=403)
