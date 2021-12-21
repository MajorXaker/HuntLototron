from django import forms

from roulette.models import Weapon
from stats.models import AmmoType, Compound, Player, Map
from .validators import InRangeValidator, ListedValueValidator, NonNegativeValidator
from django.utils.translation import gettext_lazy as _
from .models import Match


class FormAddMatch_simple(forms.Form):
    
    kills_validators = [NonNegativeValidator(_("kills")),]
    assists_validators = [NonNegativeValidator(_("assists")),]
    deaths_validators = [NonNegativeValidator(_("deaths")),]

    date = forms.DateField(
         required=True,
         input_formats = [
            '%d.%m.%y', # '16.12.21'
            '%d.%m.%Y', # '16.12.2021'
        ],
        error_messages={'invalid' : 'Date invalid. Type in date in a following format: dd.mm.yyyy'},
        
        )

    wl_status = forms.FloatField(
        label = _('Win\Loss status'), 
        validators=[ListedValueValidator((0,0.5,1))], 
        required=True,

        )

    maps = [(map,map.name) for map in Map.objects.all()]
    map = forms.ChoiceField(
        label = _('Map of the match'), 
        choices=maps, 
        required=True,
        )

    available_players = [(player.service_name(),player.get_name()) for player in Player.objects.all()]
    teammate_exists = [ListedValueValidator(available_players)] #checks that player exists
    teammate_1 = forms.ChoiceField(
        label = 'Teammate 1:', 
        choices=available_players, 
        required=True,
        disabled=True
        )
        
    teammate_2 = forms.ChoiceField(
        label = 'Teammate 2:', 
        choices=available_players, 
        required=True,
        initial = Player.objects.get(also_known_as = 'None').service_name(),
        )

    teammate_3 = forms.ChoiceField(
        label = 'Teammate 3:', 
        choices=available_players, 
        required=True,
        initial = Player.objects.get(also_known_as = 'None').service_name(),
        )
    


    bounty = forms.IntegerField(
        validators=[NonNegativeValidator('bounty')],
        required=True,
        label="Bounty taken:",
    )
    playtime = forms.DurationField(
        required=True,
        label="Match duration:",
        )

    kills_total = forms.IntegerField(
        required=True,
         validators=kills_validators,
        label="Total kills count:", #label = '',
        )

    player_1_kills = forms.IntegerField( 
        required=True,
        validators=kills_validators,
        label = 'My kills:',
        )
    player_1_assists = forms.IntegerField( 
        required=True,
        validators=assists_validators,
        label = 'My assists:',
        )
    player_1_deaths = forms.IntegerField( 
        required=True,
        validators=deaths_validators,
        label = 'My deaths:',
        )

    primary_weapons = [(weapon, weapon.name) for weapon in Weapon.objects.all()]
    player_1_primary_weapon = forms.ChoiceField(
        choices=primary_weapons, 
        required=False,
        label = 'Primary weapon:',
        )
    available_ammo = [(ammo, ammo.name) for ammo in AmmoType.objects.all()]
    player_1_primary_ammo_A = forms.ChoiceField(
        choices=available_ammo, 
        required=False,
        initial=AmmoType.objects.get(name='Standard'),
        label = 'Primary weapon ammo A:',
        )
    player_1_primary_ammo_B = forms.ChoiceField(
        choices=available_ammo, 
        required=False,
        initial=AmmoType.objects.get(name='None'),
        label = 'Primary weapon ammo B:',
        )
    
    secondary_weapons = [(weapon, weapon.name) for weapon in Weapon.objects.all()]
    player_1_secondary_weapon = forms.ChoiceField(
        choices=secondary_weapons, 
        required=False,
        label = 'Secondary weapon:',
        )
    player_1_secondary_ammo_A = forms.ChoiceField(
        choices=available_ammo, 
        required=False,
        initial=AmmoType.objects.get(name='Standard'),
        label = 'Secondary weapon ammo A:',      
        )
    player_1_secondary_ammo_B = forms.ChoiceField(
        choices=available_ammo, 
        required=False,
        initial=AmmoType.objects.get(name='None'),
        label = 'Secondary weapon ammo B:', 
        )

    compounds = [(compound.name,compound.name) for compound in Compound.objects.all()]
    #TODO add NONE compound, start compound and exit compound
    fight_locations = forms.MultipleChoiceField(
        choices=compounds,
        required=False,
        
        label = 'Fight locations',
        )




# class FormEditMatch(FormAddMatch_simple):
    

#     player_1_and_edit = {
#         'date': False,
#         'wl_status': False,
#         'teammate_1': False,
#         'teammate_2': False,
#         'teammate_3': False,
#         'bounty': False,
#         'playtime': False,
#         'kills_total': False,
#         'compounds': False,
#         'fight_locations': False,
#         'player_1_kills': False,
#         'player_1_assists': False,
#         'player_1_deaths': False,
#         'player_1_primary_weapon': False,
#         'player_1_primary_ammo_A': False,
#         'player_1_primary_ammo_B': False,
#         'player_1_secondary_weapon': False,
#         'player_1_secondary_ammo_A': False,
#         'player_1_secondary_ammo_B': False,
#         'player_2_kills': True,
#         'player_2_assists': True,
#         'player_2_deaths': True,
#         'player_2_primary_weapon': True,
#         'player_2_primary_ammo_A': True,
#         'player_2_primary_ammo_B': True,
#         'player_2_secondary_weapon': True,
#         'player_2_secondary_ammo_A': True,
#         'player_2_secondary_ammo_B': True,
#         'player_3_kills': True,
#         'player_3_assists': True,
#         'player_3_deaths': True,
#         'player_3_primary_weapon': True,
#         'player_3_primary_ammo_A': True,
#         'player_3_primary_ammo_B': True,
#         'player_3_secondary_weapon': True,
#         'player_3_secondary_ammo_A': True,
#         'player_3_secondary_ammo_B': True,        
#     }
#     player_2_and_edit = {
#         'date': True,
#         'wl_status': True,
#         'teammate_1': True,
#         'teammate_2': True,
#         'teammate_3': True,
#         'bounty': True,
#         'playtime': True,
#         'kills_total': True,
#         'compounds': True,
#         'fight_locations': True,
#         'player_1_kills': True,
#         'player_1_assists': True,
#         'player_1_deaths': True,
#         'player_1_primary_weapon': True,
#         'player_1_primary_ammo_A': True,
#         'player_1_primary_ammo_B': True,
#         'player_1_secondary_weapon': True,
#         'player_1_secondary_ammo_A': True,
#         'player_1_secondary_ammo_B': True,
#         'player_2_kills': False,
#         'player_2_assists': False,
#         'player_2_deaths': False,
#         'player_2_primary_weapon': False,
#         'player_2_primary_ammo_A': False,
#         'player_2_primary_ammo_B': False,
#         'player_2_secondary_weapon': False,
#         'player_2_secondary_ammo_A': False,
#         'player_2_secondary_ammo_B': False,
#         'player_3_kills': True,
#         'player_3_assists': True,
#         'player_3_deaths': True,
#         'player_3_primary_weapon': True,
#         'player_3_primary_ammo_A': True,
#         'player_3_primary_ammo_B': True,
#         'player_3_secondary_weapon': True,
#         'player_3_secondary_ammo_A': True,
#         'player_3_secondary_ammo_B': True,       
#     }
#     player_3_and_edit = {
#         'date': True,
#         'wl_status': True,
#         'teammate_1': True,
#         'teammate_2': True,
#         'teammate_3': True,
#         'bounty': True,
#         'playtime': True,
#         'kills_total': True,
#         'compounds': True,
#         'fight_locations': True,
#         'player_1_kills': True,
#         'player_1_assists': True,
#         'player_1_deaths': True,
#         'player_1_primary_weapon': True,
#         'player_1_primary_ammo_A': True,
#         'player_1_primary_ammo_B': True,
#         'player_1_secondary_weapon': True,
#         'player_1_secondary_ammo_A': True,
#         'player_1_secondary_ammo_B': True,
#         'player_2_kills': True,
#         'player_2_assists': True,
#         'player_2_deaths': True,
#         'player_2_primary_weapon': True,
#         'player_2_primary_ammo_A': True,
#         'player_2_primary_ammo_B': True,
#         'player_2_secondary_weapon': True,
#         'player_2_secondary_ammo_A': True,
#         'player_2_secondary_ammo_B': True,
#         'player_3_kills': False,
#         'player_3_assists': False,
#         'player_3_deaths': False,
#         'player_3_primary_weapon': False,
#         'player_3_primary_ammo_A': False,
#         'player_3_primary_ammo_B': False,
#         'player_3_secondary_weapon': False,
#         'player_3_secondary_ammo_A': False,
#         'player_3_secondary_ammo_B': False,
#     }


   
#     kills_validators = [NonNegativeValidator(_("kills")),]
#     assists_validators = [NonNegativeValidator(_("assists")),]
#     deaths_validators = [NonNegativeValidator(_("deaths")),]

#     date = forms.DateField(
#          required=True,
#          input_formats = [
#             '%d.%m.%y', # '16.12.21'
#             '%d.%m.%Y', # '16.12.2021'
#         ],
#         error_messages={'invalid' : 'Date invalid. Type in date in a following format: dd.mm.yyyy'},
        
#         )

#     wl_status = forms.FloatField(
#         label = _('Win\Loss status'), 
#         validators=[ListedValueValidator((0,0.5,1))], 
#         required=True,

#         )

#     maps = [(map,map.name) for map in Map.objects.all()]
#     map = forms.ChoiceField(
#         label = _('Map of the match'), 
#         choices=maps, 
#         required=True,
#         )

#     available_players = [(player.service_name(),player.get_name()) for player in Player.objects.all()]
#     teammate_exists = [ListedValueValidator(available_players)] #checks that player exists
#     teammate_1 = forms.ChoiceField(
#         label = 'Teammate 1:', 
#         choices=available_players, 
#         required=True,
#         disabled=True
#         )
        
#     teammate_2 = forms.ChoiceField(
#         label = 'Teammate 2:', 
#         choices=available_players, 
#         required=True,
#         initial = Player.objects.get(also_known_as = 'None').service_name(),
#         )

#     teammate_3 = forms.ChoiceField(
#         label = 'Teammate 3:', 
#         choices=available_players, 
#         required=True,
#         initial = Player.objects.get(also_known_as = 'None').service_name(),
#         )
    


#     bounty = forms.IntegerField(
#         validators=[NonNegativeValidator('bounty')],
#         required=True,
#         label="Bounty taken:",
#     )
#     playtime = forms.DurationField(
#         required=True,
#         label="Match duration:",
#         )

#     kills_total = forms.IntegerField(
#         required=True,
#          validators=kills_validators,
#         label="Total kills count:", #label = '',
#         )

#     player_1_kills = forms.IntegerField( 
#         required=True,
#         validators=kills_validators,
#         label = 'My kills:',
#         )
#     player_1_assists = forms.IntegerField( 
#         required=True,
#         validators=assists_validators,
#         label = 'My assists:',
#         )
#     player_1_deaths = forms.IntegerField( 
#         required=True,
#         validators=deaths_validators,
#         label = 'My deaths:',
#         )

#     primary_weapons = [(weapon, weapon.name) for weapon in Weapon.objects.all()]
#     player_1_primary_weapon = forms.ChoiceField(
#         choices=primary_weapons, 
#         required=False,
#         label = 'Primary weapon:',
#         )
#     available_ammo = [(ammo, ammo.name) for ammo in AmmoType.objects.all()]
#     player_1_primary_ammo_A = forms.ChoiceField(
#         choices=available_ammo, 
#         required=False,
#         initial=AmmoType.objects.get(name='Standard'),
#         label = 'Primary weapon ammo A:',
#         )
#     player_1_primary_ammo_B = forms.ChoiceField(
#         choices=available_ammo, 
#         required=False,
#         initial=AmmoType.objects.get(name='None'),
#         label = 'Primary weapon ammo B:',
#         )
    
#     secondary_weapons = [(weapon, weapon.name) for weapon in Weapon.objects.all()]
#     player_1_secondary_weapon = forms.ChoiceField(
#         choices=secondary_weapons, 
#         required=False,
#         label = 'Secondary weapon:',
#         )
#     player_1_secondary_ammo_A = forms.ChoiceField(
#         choices=available_ammo, 
#         required=False,
#         initial=AmmoType.objects.get(name='Standard'),
#         label = 'Secondary weapon ammo A:',      
#         )
#     player_1_secondary_ammo_B = forms.ChoiceField(
#         choices=available_ammo, 
#         required=False,
#         initial=AmmoType.objects.get(name='None'),
#         label = 'Secondary weapon ammo B:', 
#         )

#     compounds = [(compound.name,compound.name) for compound in Compound.objects.all()]
#     #TODO add NONE compound, start compound and exit compound
#     fight_locations = forms.MultipleChoiceField(
#         choices=compounds,
#         required=False,
        
#         label = 'Fight locations',
#         )   
    
               





#     player_2_kills = forms.IntegerField( 
#         required=True,
#         validators=kills_validators,
#         label = 'Teammate 2 kills:',
#         # disabled=lock_dict['player_1_kills'],
#         )
#     player_2_assists = forms.IntegerField( 
#         required=True,
#         validators=assists_validators,
#         label = 'Teammate 2 assists:',
#         # disabled=lock_dict['player_1_assists'],
#         )
#     player_2_deaths = forms.IntegerField( 
#         required=True,
#         validators=deaths_validators,
#         label = 'Teammate 2 deaths:',
#         # disabled=lock_dict['player_1_deaths'],
#         )


#     player_2_primary_weapon = forms.ChoiceField(
#         choices=primary_weapons, 
#         required=False,
#         label = 'Teammate 2 primary weapon:',
#         # disabled=lock_dict['player_1_primary_weapon'],
#         )
#     available_ammo = [(ammo, ammo.name) for ammo in AmmoType.objects.all()]
#     player_2_primary_ammo_A = forms.ChoiceField(
#         choices=available_ammo, 
#         required=False,
#         initial=AmmoType.objects.get(name='Standard'),
#         label = 'Teammate 2 primary weapon ammo A:',
#         # disabled=lock_dict['player_1_primary_ammo_A'],        
#         )
#     player_2_primary_ammo_B = forms.ChoiceField(
#         choices=available_ammo, 
#         required=False,
#         initial=AmmoType.objects.get(name='None'),
#         label = 'Teammate 2 primary weapon ammo B:',
#         # disabled=lock_dict['player_1_primary_ammo_B'],
#         )
    

#     player_2_secondary_weapon = forms.ChoiceField(
#         choices=secondary_weapons, 
#         required=False,
#         label = 'Teammate 2 Secondary weapon:',
#         # disabled=lock_dict['player_1_secondary_weapon'],
#         )
#     player_2_secondary_ammo_A = forms.ChoiceField(
#         choices=available_ammo, 
#         required=False,
#         initial=AmmoType.objects.get(name='Standard'),
#         label = 'Teammate 2 Secondary weapon ammo A:',
#         # disabled=lock_dict['player_1_secondary_ammo_A'],        
#         )
#     player_2_secondary_ammo_B = forms.ChoiceField(
#         choices=available_ammo, 
#         required=False,
#         initial=AmmoType.objects.get(name='None'),
#         label = 'Teammate 2 Secondary weapon ammo B:',
#         # disabled=lock_dict['player_1_secondary_ammo_B'],        
#         )

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

        



class FormRegisterPlayer(forms.Form):
    pass