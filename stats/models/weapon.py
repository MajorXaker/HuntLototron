from django.db import models
from django.utils.translation import gettext_lazy as _

from .weapon_type import WeaponType


class Weapon(models.Model):
    name = models.CharField(max_length=50, blank=False, unique=True)
    weapon_type = models.ForeignKey(
        WeaponType, on_delete=models.PROTECT, blank=False
    )  # protect forbids deletion of a higher class
    translated_title = models.CharField(max_length=50, blank=True)
    core_gun = models.CharField(max_length=50)

    sizes_types = [(1, "Small - 1"), (2, "Medium - 2"), (3, "Large - 3")]
    size = models.IntegerField(
        # max_length=10,
        choices=sizes_types,
        blank=False,
    )

    sights_types = [
        ("ironsight", "ironsight"),
        ("deadeye", "deadeye"),
        ("marksman", "marksman"),
        ("sniper", "sniper"),
        ("aperture", "aperture"),
    ]
    sights = models.CharField(max_length=50, choices=sights_types, default="ironsight")

    melee_types = [
        ("talon", "Talon"),
        ("hatchet", "Hatchet"),
        ("bayonet", "Bayonet"),
        ("mace", "Mace"),
        ("none", "None"),
        ("knukcles-duster", "Knuckles"),
    ]
    melee = models.CharField(max_length=50, choices=melee_types, default="None")

    muzzle_types = [("None", "None"), ("silencer", "Silencer")]
    muzzle = models.CharField(max_length=50, choices=muzzle_types, default="None")
    weight = models.FloatField()
    price = models.IntegerField(blank=False)

    has_ammo_B = models.BooleanField(
        _("Does this weapon have 2nd ammo type?"), default=False
    )

    def dictate(self):
        return {
            "name": self.name,
            "gun_type": str(self.gun_type),
            "translated_title": self.translated_title,
            "core_gun": self.core_gun,
            "size": self.size,
            "sights": self.sights,
            "melee": self.melee,
            "muzzle": self.muzzle,
            "weight": self.weight,
            "price": self.price,
        }

    def __str__(self) -> str:
        return self.name
