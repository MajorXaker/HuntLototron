from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class WeaponType(models.Model):
    name = models.CharField(max_length=255) #making a class for a weapon type, to use it later

    def __str__(self):
        return self.name


class Weapon(models.Model):
    name = models.CharField(max_length=50, blank=False, unique=True)
    gun_type = models.ForeignKey(WeaponType, on_delete=models.PROTECT, blank=False) #protect forbids deletion of a higher class 
    translated_title = models.CharField(max_length=50, blank=True)
    core_gun = models.CharField(max_length=50)

    sizes_types = [
            (1, 'Small - 1'),
            (2, 'Medium - 2'),
            (3, 'Large - 3')
        ]
    size = models.CharField(
        max_length=10,
        choices=sizes_types,
        blank=False
    )

    sights_types = [
            ('ironsight','ironsight'),
            ('deadeye','deadeye'),
            ('marksman','marksman'),
            ('sniper','sniper'),
            ('aperture','aperture')
        ]
    sights = models.CharField(
        max_length=50,
        choices=sights_types,
        default="ironsight"
    )

    melee_types = [
        ("talon", "Talon"),
        ("hatchet", "Hatchet"),
        ("bayonet", "Bayonet"),
        ("mace", "Mace"),
        ("none", "None"),
        ("knukcles-duster", "Knuckles")
    ]
    melee = models.CharField(
        max_length=50,
        choices=melee_types,
        default="None"
    )

    muzzle_types = [
        ("None", "None"),
        ("silencer", "Silencer")
    ]
    muzzle = models.CharField(
        max_length=50,
        choices=muzzle_types,
        default="None"
    )
    weight = models.FloatField()
    price = models.IntegerField(blank=False)

