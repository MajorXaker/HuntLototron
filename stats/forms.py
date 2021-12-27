from django import forms

from roulette.models import Weapon
from stats.models import AmmoType, Compound, Player, Map
from .validators import InRangeValidator, ListedValueValidator, NonNegativeValidator
from django.utils.translation import gettext_lazy as _
from .models import Match
from django.contrib.auth.models import User

class MatchAddForm(forms.ModelForm):
    
    class Meta:
        model = Match
        fields = (
            'date', 'wl_status', 'player_1', 'player_2', 'player_3', 'bounty', 'playtime', 'kills_total', 'fights_locations', 
            'player_1_kills', 'player_1_assists', 'player_1_deaths', 
            'player_1_primary_weapon', 'player_1_primary_ammo_A', 'player_1_primary_ammo_B', 
            'player_1_secondary_weapon', 'player_1_secondary_ammo_A', 'player_1_secondary_ammo_B'
             
        )



class MatchEditForm(forms.ModelForm):
    
    class Meta:
        model = Match
        fields = (
            'date', 'wl_status', 'player_1', 'player_2', 'player_3', 'bounty', 'playtime', 'kills_total', 'fights_locations', 
            'player_1_kills', 'player_1_assists', 'player_1_deaths', 
            'player_1_primary_weapon', 'player_1_primary_ammo_A', 'player_1_primary_ammo_B', 
            'player_1_secondary_weapon', 'player_1_secondary_ammo_A', 'player_1_secondary_ammo_B', 
            'player_2_kills', 'player_2_assists', 'player_2_deaths', 
            'player_2_primary_weapon', 'player_2_primary_ammo_A', 'player_2_primary_ammo_B', 
            'player_2_secondary_weapon', 'player_2_secondary_ammo_A', 'player_2_secondary_ammo_B', 
            'player_3_kills', 'player_3_assists', 'player_3_deaths', 
            'player_3_primary_weapon', 'player_3_primary_ammo_A', 'player_3_primary_ammo_B', 
            'player_3_secondary_weapon', 'player_3_secondary_ammo_A', 'player_3_secondary_ammo_B', 
        )
    
    
