from typing_extensions import Required
from django.core import validators
from django.db import models
from HuntLototron.auxilary import AuxClass
from roulette.models import Weapon
from django.contrib.auth.models import User
import datetime
from .validators import InRangeValidator, ListedValueValidator, SumValidator, UnicodeUsernameValidator, NonNegativeValidator, UnicodeAndSpaceValidator
from django.utils.translation import gettext_lazy as _


# Create your models here.



class Player(models.Model):

    username_validator = UnicodeUsernameValidator()
    

    username = models.OneToOneField(
        User,
        on_delete=models.SET( User.objects.get(username='UnknownHunter').pk),
        validators=[username_validator],
        related_name="username_of_player",
        null=True,
        blank=True,
        unique=False,
        )
    use_alternative_name = models.BooleanField(default=False)
    also_known_as = models.CharField(
        max_length=50, 
        verbose_name="Also known as", 
        blank=True,
        validators = [UnicodeAndSpaceValidator(),],
        
        )
    allow_see_mathes = models.BooleanField(
        _("Allow other users see your matches."),
        default=False,
        )
    allow_see_name = models.BooleanField(
        _("Allow other users see your matches and your name."),
        default=False,
        )
    show_only_my_matches = models.BooleanField(
        _("Display only matches, where you have participated."),
        default=True,
        )
    verified_user = models.BooleanField(
        _("Allow stats of this player be used in common statistics."),
        default=False,
        )

    hash_key = models.CharField(
        # It is used to bind non user profile to real user profile. So registred players could create accouts of their friends.
        # Because it's impossible to use anonymous player in matches.
        _("Hash key of this user."), 
        max_length=32,
        null=True,
        blank=True,
        )

    hash_redeemable = models.BooleanField(
        # Restriction. No one should be able to bind a real account.
        _("May be redeemed by a user"),
        default=False,
        )

    show_tooltips = models.BooleanField(
        _("States whether tooltips and usage hints are visible."),
        # TODO Tooltips
        default=True
        )
    
    created_by = models.ForeignKey(
        User, 
        verbose_name=_("Showss who is the creator of this player. It's used only while player is not assigned to a user."), 
        on_delete=models.SET( User.objects.get(username='UnknownHunter').pk),
        related_name= 'creator', # do I even need this if 'Player.objects.filter(created_by = active_user)' 
        blank = True,
        null = True,
        )

    may_be_duplicate = models.BooleanField(
        _("Allows this player to have duplicate in match. Service field."),
        default = False
        )

    

    def update(self, user):
        
        self.also_known_as = ''
        self.use_alternative_name = False
        self.username = user
        


    # def service_name(self):
    #     if self.use_alternative_name:
    #         return 'a.' + self.also_known_as
    #     else:
    #         return 'u.' + self.username.username


    encode = False

    def __str__(self) -> str:
        encode = self.encode
        if self.use_alternative_name:
            
            result =  self.also_known_as
        else:
            try:
                result =  self.username.username
            except AttributeError:
                #needed to look for players which have no username
                result = self.also_known_as

        if encode:
            return 'Player '+AuxClass.encode_md5(result)[:6]
        else:
            return result

    # def get_name(self):
    #     return str(self)
    

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
    # TODO delete kit model
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
    map = models.ForeignKey(
        Map, 
        verbose_name=_("Map of the match"), 
        on_delete=models.PROTECT,
        related_name="map_of_match",
        blank=True,
        null=True

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
        blank=True,
        )
    player_2_assists = models.IntegerField(
        default=0,
        validators=assists_validators,
        blank=True,
        )
    player_2_deaths = models.IntegerField(
        default=0,
        validators=deaths_validators,
        blank=True,
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
        blank=True,
        )
    player_3_assists = models.IntegerField(
        default=0,
        validators=assists_validators,
        blank=True,
        )
    player_3_deaths = models.IntegerField(
        default=0,
        validators=deaths_validators,
        blank=True,
        )
    player_3_signature = models.BooleanField(
        _("player 2 signature"),
        default=False,
        blank=True,
        )

    fights_locations = models.ManyToManyField(
        Compound, 
        verbose_name="Place of a firefight"
        ) 

    correct_match = models.BooleanField(
        _("Match data is correct"),
        default=False)
        
    class PlayerDuplicationError(Exception):
        '''Exception is raised when we try to assign several players which cannot have duplicates. 
        The only players which could have its own duplicates should be Unknown Hunter (aka deleted one), Random Hunter, and maybe some other.

        Atributes
            player - name\class of a player duplicate
            message (optional) - in case you'd like to change this
        '''
        def __init__(self, player, message = None, *args: object) -> None:
            
            if message == None:
                self.message = f'Player {player} does not allow duplicates!'
            else:
                self.message = message
            super().__init__(*args)


    def __str__(self) -> str:
        return "Match #"+ str(self.id)

    def players(self, is_class = False):
        '''This func puts player credentials into a list. If is_class is True then puts whole classes.
        Credentials is a bit outdated logic, use is_class instead.
        '''
        players_credentials = []
        all_players = (self.player_1, self.player_2, self. player_3)


        for player in all_players:
            try:
                username = player.username.username
            except AttributeError:
                username = ''
            try:
                playername = player.also_known_as
            except AttributeError:
                playername = ''
            players_credentials.append((username, playername))

        if not is_class:
            return players_credentials
        else:
            return all_players

    def get_player_slot(self, credentials, is_class = False, debug = False):
        '''Gets number of player's slot - 1,2 or 3 on given class of credentials
        '''
        if debug:
            print(f'Looking for {credentials} in {self}.')
        if credentials in self.players(is_class=is_class):
            position = self.players(is_class=is_class).index(credentials) + 1
            if debug:
                print(f'{credentials} found on position {position}')
            return position
        else:
            if debug:
                print(f'{credentials} not found')
            return 0



    def display_allowed(self):
        '''States whether participants allow to show this match'''
        player_1_allowed = self.player_1.allow_see_mathes
        player_2_allowed = self.player_1.allow_see_mathes
        player_3_allowed = self.player_1.allow_see_mathes

        return player_1_allowed or player_2_allowed or player_3_allowed
    
    def set_encoding(self):
        '''Enables encoding of players' names if they have not allowed others to see their names
        '''
        if not self.player_1.allow_see_name:
            self.player_1.encode = True
        try:
            if not self.player_2.allow_see_name:
                self.player_2.encode = True
        except AttributeError:
            pass
        try:
            if not self.player_3.allow_see_name:
                self.player_3.encode = True
        except AttributeError:
            pass
    
    def check_players_duplication(self, new_player, debug = False):
        '''Checks whether new player will cause player duplication. In most cases duplication is restricted

        Parameters
            new_player - class of new player

        Output
            False - if everything is OK, or raises a PlayerDuplicationError
        '''
        if new_player.may_be_duplicate:
            if debug:
                print('Player duplication allowed')
            return False
        else:
            players = self.players(is_class=True)
            if debug:
                print(f'Current players in {self}: {players}')
            if new_player in players:
                raise self.PlayerDuplicationError(new_player)
            else:
                if debug:
                    print('No duplication')
                return False

    def swap_players(self, old_player, new_player, debug = False):
        '''Swaps old and new players. In its course of work checks for duplication and raises a PlayerDuplicationError if necessary.
        
        Atributes
        ---
        1st - Old player class
        2nd - New player class
        
        '''
        position = self.get_player_slot(old_player, is_class=True, debug = True)
        
        self.check_players_duplication(new_player, debug=debug)

        if position == 1:
            self.player_1 = new_player
        elif position == 2:
            self.player_2 = new_player
        elif position == 3:
            self.player_3 = new_player
        if debug:
            print(f'Swapped player {position} with {new_player}')
            print(f'Current players: {self.player_1}, {self.player_2} and {self.player_3}.')
        