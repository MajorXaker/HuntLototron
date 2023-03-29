import datetime
import hashlib
from typing import Tuple

from django.db import models
from django.utils.translation import gettext_lazy as _

from stats.validators import ListedValueValidator, NonNegativeValidator
from . import Map, AmmoType, Compound, Player, Weapon

players_nums = {"1": False, "2": True, "3": True}


class Match(models.Model):
    # TODO validator for winloss

    wl_status = models.FloatField(
        blank=False, default=0, validators=[ListedValueValidator((0, 0.5, 1))]
    )
    date = models.DateField(default=datetime.date.today)
    kills_total = models.IntegerField(
        blank=False,
        default=0,
    )
    playtime = models.DurationField(blank=False)

    map = models.ForeignKey(
        Map,
        verbose_name=_("Map of the match"),
        on_delete=models.PROTECT,
        related_name="map_of_match",
        blank=True,
        null=True,
    )

    kills_validators = [
        NonNegativeValidator(_("kills")),
    ]
    assists_validators = [
        NonNegativeValidator(_("assists")),
    ]
    deaths_validators = [
        NonNegativeValidator(_("deaths")),
    ]
    bounty_validators = [
        NonNegativeValidator(_("bounty")),
    ]

    # each player have it's own data fields
    # player 1 is mandatory - he creates a match class instance
    player_1 = models.ForeignKey(Player, on_delete=models.PROTECT, related_name='player_1_name', null=False, blank=False)

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
        default=None,
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
                                                  default=None,
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
    player_1_bounty = models.IntegerField(
        _("player 1 bounty"),
        default=0,
        validators=bounty_validators,
        null=False,
        blank=True,
    )
    player_1_signature = models.BooleanField(
        _("player 1 signature"),
        default=False,
        blank=True,
    )  # this fiels certifies that player 1 privided his side of data
    # it is needed when we try to calculate the data for a player
    # so only the matches he gave info for would be taken into account

    # other players info may be also given
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
        # default=AmmoType.objects.get(name="Standard").id,
        null=True,
        blank=True,
    )
    player_2_primary_ammo_B = models.ForeignKey(
        AmmoType,
        on_delete=models.PROTECT,
        related_name='player_2_primary_weapon_ammo_B',
        default=None,
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
                                                  # default=AmmoType.objects.get(name="Standard").id,
                                                  null=True,
                                                  blank=True,
                                                  )
    player_2_secondary_ammo_B = models.ForeignKey(AmmoType,
                                                  on_delete=models.PROTECT,
                                                  related_name='player_2_secondary_weapon_ammo_B',
                                                  default=None,
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
    player_2_bounty = models.IntegerField(
        _("player 2 bounty"),
        default=0,
        validators=bounty_validators,
        null=False,
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
        # default=AmmoType.objects.get(name="Standard").id,
        null=True,
        blank=True,
    )
    player_3_primary_ammo_B = models.ForeignKey(
        AmmoType,
        on_delete=models.PROTECT,
        related_name='player_3_primary_weapon_ammo_B',
        # default=AmmoType.objects.get(name="None").id,
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
                                                  # default=AmmoType.objects.get(name="Standard").id,
                                                  null=True,
                                                  blank=True,
                                                  )
    player_3_secondary_ammo_B = models.ForeignKey(AmmoType,
                                                  on_delete=models.PROTECT,
                                                  related_name='player_3_secondary_weapon_ammo_B',
                                                  # default=AmmoType.objects.get(name="None").id,
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
    player_3_bounty = models.IntegerField(
        _("player 3 bounty"),
        default=0,
        validators=bounty_validators,
        null=False,
        blank=True,
    )
    player_3_signature = models.BooleanField(
        _("player 2 signature"),
        default=False,
        blank=True,
    )

    fights_locations = models.ManyToManyField(
        Compound,
        verbose_name=_("Place of a firefight")
    )

    correct_match = models.BooleanField(_("Match data is correct"), default=False)

    external = models.BooleanField(_("Externally added match"), default=False)

    class PlayerDuplicationError(Exception):
        """Exception is raised when we try to assign several players which cannot have duplicates.
        The only players which could have its own duplicates should be Unknown Hunter (aka deleted one), Random Hunter,
         and maybe some other.

        Atributes
            player - name or class of a player duplicate
            message (optional) - in case you'd like to change this
        """

        def __init__(self, player, message=None, *args: object) -> None:
            if message is None:
                self.message = f"Player {player} does not allow duplicates!"
            else:
                self.message = message
            super().__init__(*args)

    def __str__(self) -> str:
        return "Match #" + str(self.id)

    def get_md5(self) -> str:
        values = [
            self.date,
            self.playtime,
            self.map,
            self.player_1,
            self.player_2,
            self.player_3,
            self.player_1_bounty,
            self.player_2_bounty,
            self.player_3_bounty,
            self.player_1_primary_weapon,
            self.player_1_secondary_weapon,
            self.fights_locations,
        ]
        str_values = [str(val) for val in values]
        hashable_str = bytes("".join(str_values), encoding="utf-8")
        hashed = hashlib.md5()
        hashed.update(hashable_str)
        encoded = hashed.hexdigest()
        return encoded

    def players(self) -> Tuple[Player, Player | None, Player | None]:
        """This func puts player classes into a tuple."""
        return self.player_1, self.player_2 or None, self.player_3 or None

    def get_player_slot(self, player_lookup: Player):
        """Gets number of player's slot - 1,2 or 3 on given class of credentials"""
        players = self.players()
        if player_lookup in players:
            position = players.index(player_lookup) + 1
            return position

    def display_allowed(self):
        """States whether participants allow to show this match"""
        player_1_allowed = self.player_1.allow_see_mathes
        player_2_allowed = self.player_1.allow_see_mathes
        player_3_allowed = self.player_1.allow_see_mathes

        return player_1_allowed or player_2_allowed or player_3_allowed

    def set_encoding(self):
        """Enables encoding of players' names if they have not allowed others to see their names"""
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

    def check_players_duplication(self, new_player, debug=False):
        """Checks whether new player will cause player duplication. In most cases duplication is restricted

        Parameters
            new_player - class of new player

        Output
            False - if everything is OK, or raises a PlayerDuplicationError
        """
        if new_player.may_be_duplicate:
            if debug:
                print("Player duplication allowed")
            return
        players = self.players()
        if debug:
            print(f"Current players in {self}: {players}")
        if new_player in players:
            raise self.PlayerDuplicationError(new_player)
        if debug:
            print("No duplication")

    def swap_players(self, old_player, new_player, debug=False):
        """Swaps old and new players. In its course of work checks for duplication and raises
         a PlayerDuplicationError if necessary.

        Attributes
        ---
        1st - Old player class
        2nd - New player class

        """
        position = self.get_player_slot(old_player, debug=debug)

        self.check_players_duplication(new_player, debug=debug)

        setattr(self, f"player_{position}", new_player)

        if debug:
            print(f"Swapped player {position} with {new_player}")
            print(
                f"Current players: {self.player_1}, {self.player_2} and {self.player_3}."
            )

    # was used in a single print statement
    # TODO implement match validator
    # def verify_guns(self, player_slot):
    #     weapons = {
    #         1: (self.player_1_primary_weapon, self.player_1_secondary_weapon),
    #         2: (self.player_2_primary_weapon, self.player_2_secondary_weapon),
    #         3: (self.player_3_primary_weapon, self.player_3_secondary_weapon)
    #     }
    #     ammo = {
    #         1: (self.player_1_primary_ammo_A, self.player_1_primary_ammo_B, self.player_1_secondary_ammo_A,
    #             self.player_1_secondary_ammo_B),
    #         2: (self.player_2_primary_ammo_A, self.player_2_primary_ammo_B, self.player_2_secondary_ammo_A,
    #             self.player_2_secondary_ammo_B),
    #         3: (self.player_3_primary_ammo_A, self.player_3_primary_ammo_B, self.player_3_secondary_ammo_A,
    #             self.player_3_secondary_ammo_B)
    #     }
    #
    #     good_check = {
    #         'Correct primary ammo A': ammo[player_slot][0] is not None,
    #         'Correct secondary ammo A': ammo[player_slot][2] is not None,
    #         'Correct primary ammo B': ammo[player_slot][1] is not None if weapons[player_slot][0].has_ammo_B else
    #         ammo[player_slot][1] is None,
    #         'Correct secondary ammo B': ammo[player_slot][3] is not None if weapons[player_slot][1].has_ammo_B else
    #         ammo[player_slot][3] is None,
    #         'Guns not exceed 5 slot limit': True if weapons[player_slot][0].size + weapons[player_slot][
    #             1].size < 6 else False
    #     }
    #
    #     return False in good_check.values(), good_check
