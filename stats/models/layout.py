from django.db import models
from .slots import Slots

from .weapon_type import WeaponType


class Layout(models.Model):
    layout_type = models.ForeignKey(
        Slots, on_delete=models.PROTECT, blank=False, default="3+1"
    )
    primary_type = models.ForeignKey(
        WeaponType,
        on_delete=models.PROTECT,
        blank=False,
        related_name="primary_weapon_type",
    )
    secondary_type = models.ForeignKey(
        WeaponType,
        on_delete=models.PROTECT,
        blank=False,
        related_name="secondary_weapon_type",
    )
    weight = models.FloatField(default=1)

    def __str__(self):
        return str(self.primary_type) + " + " + str(self.secondary_type)

    def dictate(self):
        return {
            "layout_type": self.layout_type,
            "primary_type": self.primary_type,
            "secondary_type": self.secondary_type,
            "chance": self.chance,
            "name": str(self.primary_type) + " + " + str(self.secondary_type),
        }
