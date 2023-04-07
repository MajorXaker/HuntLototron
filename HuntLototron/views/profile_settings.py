from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render
from django.views import View

from HuntLototron.forms import CreateHashInvite, RedeemHashInvite, UserSettingsForm
from config import settings as s
from stats import models as m
from utils.get_credentials import UserCredsOrganised
from utils.invite_codes import create_code


class ProfileSettings(LoginRequiredMixin, View):
    user: UserCredsOrganised
    page = "registration/profile_settings.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.additional_data = {}

    def get(self, request):
        self.user = UserCredsOrganised.from_request(request)
        player = User.objects.get(username=self.user.username).username_of_player

        active_user_invited = m.Player.objects.filter(created_by=self.user.user)

        form_create_hash = CreateHashInvite()
        form_redeem_invite = RedeemHashInvite()
        form_settings = UserSettingsForm(instance=player)

        context = {
            "user": self.user,
            "form_settings": form_settings,
            "form_invites": form_create_hash,
            "form_redeem": form_redeem_invite,
            "invites": active_user_invited,
        }
        return render(request, self.page, context)

    def post(self, request):
        self.user = UserCredsOrganised.from_request(request)

        active_user_invited = m.Player.objects.filter(created_by=self.user.user)

        form_create_hash = CreateHashInvite(request.POST)
        form_redeem_invite = RedeemHashInvite(request.POST)
        form_settings = UserSettingsForm(request.POST)

        if "settings_update" in request.POST.keys():
            form_settings = self.update_settings(form_settings)
        if "hash_create" in request.POST.keys():
            form_create_hash = self.create_hash_invite(form_create_hash)
        elif "hash_redeem" in request.POST.keys():
            form_redeem_invite = self.redeem_hash_invite(form_redeem_invite)

        context = {
            "user": self.user,
            "form_invites": form_create_hash,
            "form_settings": form_settings,
            "invites": active_user_invited,
            "form_redeem": form_redeem_invite,
            "additional": self.additional_data,
        }

        return render(request, self.page, context)

    def update_settings(self, form_settings):
        if form_settings.is_valid():
            new_aka = form_settings.cleaned_data["also_known_as"]
            if not new_aka:
                self.user.player.use_alternative_name = False
                self.user.player.also_known_as = None
            else:
                self.user.player.use_alternative_name = True
                self.user.player.also_known_as = new_aka

            self.user.player.allow_see_mathes = form_settings.cleaned_data["allow_see_mathes"]
            self.user.player.allow_see_name = form_settings.cleaned_data["allow_see_name"]
            self.user.player.show_only_my_matches = form_settings.cleaned_data[
                "show_only_my_matches"
            ]
            self.user.player.save()

            self.user.name = form_settings.cleaned_data["also_known_as"]
            self.additional_data = {"changed": True}
        return form_settings

    def create_hash_invite(self, form_create_hash):
        if form_create_hash.is_valid():
            hashes_created = len(m.Player.objects.filtem.r(created_by_id=self.user.user))
            if hashes_created > s.USER_HASH_LIMIT:
                form_create_hash.add_error(None, f"You have used all your hash invites: {s.USER_HASH_LIMIT}")
                return form_create_hash
            new_player_name = form_create_hash.cleaned_data["player_name"]

            player_invited = m.Player(
                hash_redeemable=True,
                hash_key=create_code(),
                created_by=self.user.user,
                also_known_as=new_player_name,
                use_alternative_name=True
            )
            player_invited.save()
            form_create_hash = CreateHashInvite()
        return form_create_hash

    def redeem_hash_invite(self, additional, form_redeem_invite):
        if form_redeem_invite.is_valid():
            hashed_player = m.Player.objects.get(
                hash_key=form_redeem_invite.cleaned_data["hash_key"]
            )

            if hashed_player.created_by == self.user.user:
                form_redeem_invite = RedeemHashInvite()
                form_redeem_invite.add_error("hash_key", "You cannot redeem your own hash-invite")
                # additional["is_redeem_message"] = True
                #
                # additional[
                #     "redeem_message"
                # ] = f"You cannot redeem your own hash-invite."
            else:
                hashed_player_matches = m.Match.objects.filter(
                    Q(player_1=hashed_player)
                    | Q(player_2=hashed_player)
                    | Q(player_3=hashed_player)
                )
                try:
                    [
                        match.swap_players(hashed_player, self.user.username)
                        for match in hashed_player_matches
                    ]
                except m.Match.PlayerDuplicationError:
                    additional["is_redeem_message"] = True
                    additional[
                        "redeem_message"
                    ] = f"Redeeming this hash-invite would lead to player duplication in match. Redeem denied."
                else:
                    [match.save() for match in hashed_player_matches]
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
        return form_redeem_invite
