from _operator import attrgetter
from itertools import chain

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render

from stats import models as m
from stats.utils.get_credentials import get_credentials


@login_required
def show_stats_table(request: WSGIRequest):
    user = get_credentials(request)

    if not request.user.is_staff:
        # we need to know whose matches are we looking for
        if user["has_aka"]:
            look_for_user = m.Player.objects.get(also_known_as=user["playername"])
        else:
            look_for_user = User.objects.get(
                username=user["username"]
            ).username_of_player

        # 3 queries with the name of active player
        p1_group = m.Match.objects.filter(player_1=look_for_user)
        p2_group = m.Match.objects.filter(player_2=look_for_user)
        p3_group = m.Match.objects.filter(player_3=look_for_user)

        if request.user.username_of_player.show_only_my_matches:
            filtered_matches = []
        else:
            # other matches group
            all_matches = m.Match.objects.all()
            filtered_matches = [
                match for match in all_matches if match.display_allowed()
            ]
            hashed_matches = [match.set_encoding() for match in filtered_matches]

        # results are sorted by their id
        result_as_list = sorted(
            chain(p1_group, p2_group, p3_group, filtered_matches), key=attrgetter("id")
        )

        result_as_set = set(result_as_list)
        result_ready = list(result_as_set)
        result_ready.reverse()

    else:
        result_ready = m.Match.objects.all()

    response = render(
        request, "stats_list.html", {"matches": result_ready, "user": user}
    )
    return response
