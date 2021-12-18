from typing_extensions import Required
from django.core import validators
from django.db import models
from roulette.models import Weapon
from django.contrib.auth.models import User
import datetime
from .validators import InRangeValidator, ListedValueValidator, SumValidator, UnicodeUsernameValidator, NonNegativeValidator
from django.utils.translation import gettext_lazy as _

# Create your models here.



class Player(models.Model):

    username_validator = UnicodeUsernameValidator()

    username = models.OneToOneField(
        User,
        on_delete=models.SET("Unknown player"),
        validators=[username_validator],
        related_name="player_username",)
    use_alternative_name = models.BooleanField(default=False)
    also_known_as = models.CharField(
        max_length=50, 
        verbose_name="Also known as", 
        blank=True,
        validators = [username_validator,]
        )

    kills_count = models.IntegerField(blank=False, default=0)
    asissts_count = models.IntegerField(blank=False, default=0)
    deaths_count = models.IntegerField(blank=False, default=0)

    def service_name(self):
        if self.use_alternative_name:
            return 'a.' + self.also_known_as
        else:
            return 'u.' + self.username.username

    def get_kda_ratio(self):
        return (self.kills_count + self.asissts_count) / self.deaths_count

    def get_kd_ratio(self):
        return self.kills_count / self.deaths_count

    #this methods ruins form use, try to find another way
    def __str__(self) -> str:
        if self.use_alternative_name:
            return self.also_known_as
        else:
            return self.username.username

    def get_name(self):
        # if self.use_alternative_name:
        #     return self.also_known_as
        # else:
        #     return self.username.username
        return str(self)
    

class AmmoType(models.Model):
    name = models.CharField(max_length=50, blank=False)

    def __str__(self) -> str:
        return self.name

class Map(models.Model):
    name = models.CharField(primary_key=True, max_length=80)


    def __str__(self) -> str:
        return self.name


class Compound(models.Model):
    name = models.CharField(primary_key=True, max_length=80)
    from_map = models.ForeignKey(Map, verbose_name="Map", on_delete=models.PROTECT, default=None)
    double_clue = models.BooleanField()
    #idk why i may need theese, but i create it for later
    #atm these values are used in JS, stil i doubt that it's a good idea to pull them every time from DB
    #yet if i need to correct them i'll just correct values in db
    #it will require wiring frontend js to db
    x_relative = models.FloatField(default= -2)
    y_relative = models.FloatField(default= -2)

    def __str__(self) -> str:
        return self.from_map.name + " - " + self.name

    



class Kit(models.Model):
    #if kit does not exist - create it, if exists - increase its popularity
    primary_weapon = models.ForeignKey(Weapon, on_delete=models.PROTECT, related_name='primary_weapon')
    primary_ammo_A = models.ForeignKey(AmmoType, on_delete=models.PROTECT, related_name='primary_weapon_ammo_A', default=AmmoType.objects.get(name="Standard").id)
    primary_ammo_B = models.ForeignKey(AmmoType, on_delete=models.PROTECT, related_name='primary_weapon_ammo_B', default=AmmoType.objects.get(name="None").id)
    secondary_weapon = models.ForeignKey(Weapon, on_delete=models.PROTECT, related_name='secondary_weapon')
    secondary_ammo_A = models.ForeignKey(AmmoType, on_delete=models.PROTECT, related_name='secondary_weapon_ammo_A', default=AmmoType.objects.get(name="Standard").id)
    secondary_ammo_B = models.ForeignKey(AmmoType, on_delete=models.PROTECT, related_name='secondary_weapon_ammo_B', default=AmmoType.objects.get(name="None").id)

    popularity = models.IntegerField(default=0)

    


    
    def __str__(self) -> str:

        def using_ammo(ammo_a, ammo_b):
            ammos = [ammo_a, ammo_b]
            ammo_2_ignore = [
                AmmoType.objects.get(name="Standard"),
                AmmoType.objects.get(name="None")
            ]
            ammos = [ammo.name for ammo in ammos if ammo not in ammo_2_ignore]

            if len(ammos) == 0:
                return ""
            else:
                return " ("+"+".join(ammos)+")"    
        return self.primary_weapon.name + using_ammo(self.primary_ammo_A, self.primary_ammo_B) + " + " + self.secondary_weapon.name + using_ammo(self.secondary_ammo_A, self.secondary_ammo_B)
    


class Match(models.Model):
    #TODO validator for winloss

    wl_status = models.FloatField(
        blank=False, 
        default=0,
        validators=[ListedValueValidator((0,0.5,1))]
        )
    date = models.DateField(  default=datetime.date.today)
    kills_total = models.IntegerField(
        blank=False, 
        default=0
        
        )
    playtime = models.DurationField(blank=False)
    bounty = models.IntegerField(
        _("bounty"), 
        null=False,
        default=0,
        validators=[NonNegativeValidator('bounty'),],

        )

    kills_validators = [NonNegativeValidator(_('kills')),]
    assists_validators = [NonNegativeValidator(_("assists")),]
    deaths_validators = [NonNegativeValidator(_("deaths")),]
    
    #each player have it's own data fields
    #player 1 is mandatory - he creates a match class instance
    player_1 = models.ForeignKey(Player, on_delete=models.PROTECT, related_name='player_1_name')

    player_1_primary_weapon = models.ForeignKey(
        Weapon, 
        on_delete=models.PROTECT, 
        related_name='player_1_primary_weapon',
        null=True,
        )
    player_1_primary_ammo_A = models.ForeignKey(
        AmmoType, 
        on_delete=models.PROTECT, 
        related_name='player_1_primary_weapon_ammo_A', 
        default=AmmoType.objects.get(name="Standard").id,
        null=True,
        )
    player_1_primary_ammo_B = models.ForeignKey(
        AmmoType, 
        on_delete=models.PROTECT, 
        related_name='player_1_primary_weapon_ammo_B', 
        default=AmmoType.objects.get(name="None").id,
        null=True,
        blank=True,
        )

    player_1_secondary_weapon = models.ForeignKey(
        Weapon, 
        on_delete=models.PROTECT, 
        related_name='player_1_secondary_weapon',
        null=True,

        )
    player_1_secondary_ammo_A = models.ForeignKey(AmmoType, on_delete=models.PROTECT, 
        related_name='player_1_secondary_weapon_ammo_A', 
        default=AmmoType.objects.get(name="Standard").id,
        null=True,

        )
    player_1_secondary_ammo_B = models.ForeignKey(AmmoType, 
        on_delete=models.PROTECT, 
        related_name='player_1_secondary_weapon_ammo_B', 
        default=AmmoType.objects.get(name="None").id,
        null=True,
        blank=True,
        )

    player_1_kills = models.IntegerField(
        default=0,
        validators=kills_validators,
        )
    player_1_assists = models.IntegerField(
        default=0,
        validators=assists_validators,
        )
    player_1_deaths = models.IntegerField(
        default=0,
        validators=deaths_validators,
        )
    player_1_signature = models.BooleanField(
        _("player 1 signature"),
        default=False,
        blank=True,
        ) #this fiels certifies that player 1 privided his side of data
        #it is needed when we try to calculate the data for a player
        #so only the matches he gave info for would be taken into account


    #other players info may be also given
    player_2 = models.ForeignKey(Player, 
        on_delete=models.PROTECT, 
        related_name='player_2_name', 
        null=True, 
        blank=True
    )
    player_2_primary_weapon = models.ForeignKey(
        Weapon, 
        on_delete=models.PROTECT, 
        related_name='player_2_primary_weapon',
        null=True,
        blank=True,
       
        )
    player_2_primary_ammo_A = models.ForeignKey(
        AmmoType, 
        on_delete=models.PROTECT, 
        related_name='player_2_primary_weapon_ammo_A', 
        default=AmmoType.objects.get(name="Standard").id,
        null=True,
        blank=True,
        )
    player_2_primary_ammo_B = models.ForeignKey(
        AmmoType, 
        on_delete=models.PROTECT, 
        related_name='player_2_primary_weapon_ammo_B', 
        default=AmmoType.objects.get(name="None").id,
        null=True,
        blank=True,
        )

    player_2_secondary_weapon = models.ForeignKey(
        Weapon, 
        on_delete=models.PROTECT, 
        related_name='player_2_secondary_weapon',
        null=True,
        blank=True,
        )
    player_2_secondary_ammo_A = models.ForeignKey(AmmoType, on_delete=models.PROTECT, 
        related_name='player_2_secondary_weapon_ammo_A', 
        default=AmmoType.objects.get(name="Standard").id,
        null=True,
        blank=True,
        )
    player_2_secondary_ammo_B = models.ForeignKey(AmmoType, 
        on_delete=models.PROTECT, 
        related_name='player_2_secondary_weapon_ammo_B', 
        default=AmmoType.objects.get(name="None").id,
        null=True,
        blank=True,
        )

    player_2_kills = models.IntegerField(
        default=0,
        validators=kills_validators,
        )
    player_2_assists = models.IntegerField(
        default=0,
        validators=assists_validators,
        )
    player_2_deaths = models.IntegerField(
        default=0,
        validators=deaths_validators,
        )
    player_2_signature = models.BooleanField(
        _("player 2 signature"),
        default=False,
        blank=True,
        )


    player_3 = models.ForeignKey(Player, 
        on_delete=models.PROTECT, 
        related_name='player_3_name', 
        null=True, 
        blank=True)

    player_3_primary_weapon = models.ForeignKey(
        Weapon, 
        on_delete=models.PROTECT, 
        related_name='player_3_primary_weapon',
        null=True,
        blank=True,
        )
    player_3_primary_ammo_A = models.ForeignKey(
        AmmoType, 
        on_delete=models.PROTECT, 
        related_name='player_3_primary_weapon_ammo_A', 
        default=AmmoType.objects.get(name="Standard").id,
        null=True,
        blank=True,
        )
    player_3_primary_ammo_B = models.ForeignKey(
        AmmoType, 
        on_delete=models.PROTECT, 
        related_name='player_3_primary_weapon_ammo_B', 
        default=AmmoType.objects.get(name="None").id,
        null=True,
        blank=True,
        )

    player_3_secondary_weapon = models.ForeignKey(
        Weapon, 
        on_delete=models.PROTECT, 
        related_name='player_3_secondary_weapon',
        null=True,
        blank=True,
        )
    player_3_secondary_ammo_A = models.ForeignKey(AmmoType, on_delete=models.PROTECT, 
        related_name='player_3_secondary_weapon_ammo_A', 
        default=AmmoType.objects.get(name="Standard").id,
        null=True,
        blank=True,
        )
    player_3_secondary_ammo_B = models.ForeignKey(AmmoType, 
        on_delete=models.PROTECT, 
        related_name='player_3_secondary_weapon_ammo_B', 
        default=AmmoType.objects.get(name="None").id,
        null=True,
        blank=True,
        )

    player_3_kills = models.IntegerField(
        default=0,
        validators=kills_validators,
        )
    player_3_assists = models.IntegerField(
        default=0,
        validators=assists_validators,
        )
    player_3_deaths = models.IntegerField(
        default=0,
        validators=deaths_validators,
        )
    player_3_signature = models.BooleanField(
        _("player 2 signature"),
        default=False,
        blank=True,
        )

    fights_locations = models.ManyToManyField(Compound, verbose_name="Place of a firefight")


    def __str__(self) -> str:
        return "Match #"+ str(self.id)