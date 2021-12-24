from django import forms

from roulette.models import Weapon
from stats.models import AmmoType, Compound, Player, Map
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from stats.models import Player




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
  