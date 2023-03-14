import hashlib

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from stats.validators import UnicodeUsernameValidator, UnicodeAndSpaceValidator


class Player(models.Model):
    def encode_md5(self, *strings):
        '''Connects any number of values into a single string, then MD5es it.
        Returns 32 char hex string. Truncate it if you need.
        '''
        s_combined = ''.join(strings)
        s_unspaced = [char for char in s_combined if char != ' ']
        s_bytes = bytes(''.join(s_unspaced), encoding='utf-8')
        code = hashlib.md5()
        code.update(s_bytes)
        encoded = code.hexdigest()
        return encoded


    username_validator = UnicodeUsernameValidator()


    username = models.OneToOneField(
        User,
        # on_delete=models.SET( User.objects.get(username='UnknownHunter').pk),
        on_delete=models.PROTECT,
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
            return 'Player '+ self.encode_md5(result)[:6]
        else:
            return result

    # def get_name(self):
    #     return str(self)
