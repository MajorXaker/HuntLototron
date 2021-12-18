from django import forms

from roulette.models import Weapon
from stats.models import AmmoType, Compound, Player
from .validators import InRangeValidator, ListedValueValidator, NonNegativeValidator
from django.utils.translation import gettext_lazy as _

class FormAddMatch_simple(forms.Form):

    kills_validators = [NonNegativeValidator(_("kills")),]
    assists_validators = [NonNegativeValidator(_("assists")),]
    deaths_validators = [NonNegativeValidator(_("deaths")),]
    available_players = [(player.service_name(),player.get_name()) for player in Player.objects.all()]
    teammate_exists = [ListedValueValidator(available_players)] #checks that player exists

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

    teammate_1 = forms.ChoiceField(
        label = 'Teammate 1:', 
        choices=available_players, 
        required=True,
        # initial='None'
        )
        
    teammate_2 = forms.ChoiceField(
        label = 'Teammate 2:', 
        choices=available_players, 
        required=True)
    teammate_3 = forms.ChoiceField(
        label = 'Teammate 3:', 
        choices=available_players, 
        required=True)
    


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

    player_kills = forms.IntegerField( 
        required=True,
        validators=kills_validators,
        label = 'My kills:',
        )
    player_assists = forms.IntegerField( 
        required=True,
        validators=assists_validators,
        label = 'My assists:',
        )
    player_deaths = forms.IntegerField( 
        required=True,
        validators=deaths_validators,
        label = 'My deaths:',
        )

    primary_weapons = [(weapon, weapon.name) for weapon in Weapon.objects.all()]
    primary_weapon = forms.ChoiceField(
        choices=primary_weapons, 
        required=False,
        label = 'Primary weapon:',
        )
    available_ammo = [(ammo, ammo.name) for ammo in AmmoType.objects.all()]
    primary_ammo_A = forms.ChoiceField(
        choices=available_ammo, 
        required=False,
        initial=AmmoType.objects.get(name='Standard'),
        label = 'Primary weapon ammo A:',        
        )
    primary_ammo_B = forms.ChoiceField(
        choices=available_ammo, 
        required=False,
        initial=AmmoType.objects.get(name='None'),
        label = 'Primary weapon ammo B:',
        )
    
    secondary_weapons = [(weapon, weapon.name) for weapon in Weapon.objects.all()]
    secondary_weapon = forms.ChoiceField(
        choices=secondary_weapons, 
        required=False,
        label = 'Secondary weapon:',
        )
    secondary_ammo_A = forms.ChoiceField(
        choices=available_ammo, 
        required=False,
        initial=AmmoType.objects.get(name='Standard'),
        label = 'Secondary weapon ammo A:',        
        )
    secondary_ammo_B = forms.ChoiceField(
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

