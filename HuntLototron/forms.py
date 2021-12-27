from django import forms

from roulette.models import Weapon
from stats.models import AmmoType, Compound, Player, Map
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from stats.models import Player
from stats.validators import UniqueAKAValidator, HashkeyExists




class RegistrationFormA(UserCreationForm):
    email = forms.EmailField(
        max_length=254, 
        required=False,
        help_text='Optional. Will be used to restore a password.'
        )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )



class UserSettingsForm(forms.ModelForm):
    class Meta:
        fields = ('also_known_as', 'allow_see_mathes', 'allow_see_name', 'show_only_my_matches')
      
        model = Player

class CreateHashInvite(forms.Form):
    player_name = forms.CharField(
        # _('Friend name. You cannot change it later, only if your buddy reclaims th'), 
        max_length=50, 
        required=False,
        validators= [UniqueAKAValidator(Player, "Player with this name already exists."),],
        )


class RedeemHashInvite(forms.Form):
    hash_key = forms.CharField(
        # _('Key invite from the other player.'),
        max_length=32,
        required=False,
        validators = [HashkeyExists(Player, 'Hash invite is not found or already redeemed.'),],
        
        )