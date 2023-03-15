from itertools import chain

from django.contrib.auth.models import User
from django.shortcuts import render
from django.views import View

from HuntLototron.auxilary import AuxClass
from HuntLototron.forms import CreateHashInvite, RedeemHashInvite, UserSettingsForm
from stats.models import Player, Match


class ProfileSettings(View):
    def get(self, request):
        user = AuxClass.credentials_to_dict(request)
        player = User.objects.get(username=user["username"]).username_of_player

        active_user = user["user"]
        active_user_invited = Player.objects.filter(created_by=active_user)

        form_create_hash = CreateHashInvite()
        form_redeem_invite = RedeemHashInvite()
        form_settings = UserSettingsForm(instance=player)

        context = {
            "user": user,
            "form_settings": form_settings,
            "form_invites": form_create_hash,
            "form_redeem": form_redeem_invite,
            "invites": active_user_invited,
        }
        return render(request, "registration/profile_settings.html", context)

    def post(self, request):
        user = AuxClass.credentials_to_dict(request)
        additional = {}  # dict for sending strings to front

        active_user = user["user"]
        active_user_invited = Player.objects.filter(created_by=active_user)

        form_create_hash = CreateHashInvite(request.POST)
        form_redeem_invite = RedeemHashInvite(request.POST)
        form_settings = UserSettingsForm(request.POST)

        if "settings_update" in request.POST.keys():
            user = AuxClass.credentials_to_dict(request)

            player = User.objects.get(username=user["username"]).username

            if form_settings.is_valid():
                player.also_known_as = form_settings.cleaned_data["also_known_as"]
                player.allow_see_mathes = form_settings.cleaned_data["allow_see_mathes"]
                player.allow_see_name = form_settings.cleaned_data["allow_see_name"]
                player.show_only_my_matches = form_settings.cleaned_data[
                    "show_only_my_matches"
                ]
                player.use_alternative_name = True

                player.save()

                user["name"] = form_settings.cleaned_data["also_known_as"]

            additional = {"changed": True}

        if "hash_create" in request.POST.keys():
            if form_create_hash.is_valid():
                new_player_name = form_create_hash.cleaned_data["player_name"]
                hash_invite = AuxClass.encode_md5(new_player_name, user["name"])

                player_invited = Player()
                player_invited.hash_key = hash_invite
                player_invited.created_by = (
                    request.user
                )  # now you have no limits on the amounts of invites
                # TODO implement limits
                player_invited.also_known_as = new_player_name
                player_invited.hash_redeemable = True
                player_invited.use_alternative_name = True
                player_invited.save()
                form_create_hash = CreateHashInvite()

        elif "hash_redeem" in request.POST.keys():
            if form_redeem_invite.is_valid():
                hashed_player = Player.objects.get(
                    hash_key=form_redeem_invite.cleaned_data["hash_key"]
                )

                if hashed_player.created_by == active_user:
                    form_redeem_invite = RedeemHashInvite()
                    additional["is_redeem_message"] = True

                    additional[
                        "redeem_message"
                    ] = f"You cannot redeem your own hash-invite."
                else:
                    matches_with_hashed_player_as_1 = Match.objects.filter(
                        player_1=hashed_player
                    )
                    matches_with_hashed_player_as_2 = Match.objects.filter(
                        player_2=hashed_player
                    )
                    matches_with_hashed_player_as_3 = Match.objects.filter(
                        player_3=hashed_player
                    )
                    matches_with_hashed_player = list(
                        chain(
                            matches_with_hashed_player_as_1,
                            matches_with_hashed_player_as_2,
                            matches_with_hashed_player_as_3,
                        )
                    )

                    try:
                        [
                            match.swap_players(hashed_player, active_user.username)
                            for match in matches_with_hashed_player
                        ]
                    except Match.PlayerDuplicationError:
                        additional["is_redeem_message"] = True
                        additional[
                            "redeem_message"
                        ] = f"Redeeming this hash-invite would lead to player duplication in match. Redeem denied."
                    else:
                        [match.save() for match in matches_with_hashed_player]
                        hashed_player.delete()
                        additional["is_redeem_message"] = True
                        additional["redeem_message"] = "Hash-invite has been redeemed."
                        form_redeem_invite = RedeemHashInvite()
            else:
                additional["is_redeem_message"] = True
                additional[
                    "redeem_message"
                ] = "Hash invite is not found or already redeemed."
                form_redeem_invite = RedeemHashInvite()

        context = {
            "user": user,
            "form_invites": form_create_hash,
            "form_settings": form_settings,
            "invites": active_user_invited,
            "form_redeem": form_redeem_invite,
            "additional": additional,
        }

        # return render (request, "registration/profile.html", context)
        return render(request, "registration/profile_settings.html", context)
