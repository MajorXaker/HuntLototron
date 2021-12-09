# from typing_extensions import Required
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.fields import CharField

# Create your models here.

class WeaponType(models.Model):
    name = models.CharField(max_length=255) #making a class for a weapon type, to use it later

    def __str__(self):
        return self.name


class Weapon(models.Model):
    name = models.CharField(max_length=50, blank=False, unique=True)
    weapon_type = models.ForeignKey(WeaponType, on_delete=models.PROTECT, blank=False) #protect forbids deletion of a higher class 
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

    def dictate(self):
        return {
            'name' : self.name,
            'gun_type' : str(self.gun_type),
            'translated_title' : self.translated_title,
            'core_gun' : self.core_gun,

            'size' : self.size,
            'sights' : self.sights,
            'melee' : self.melee,

            'muzzle' : self.muzzle,
            'weight' : self.weight,
            'price' : self.price
        }
    
    def __str__(self) -> str:
        return self.name

class Slots(models.Model):
    # layout_list = [
    #     ("3+2","3+2"),
    #     ("2+2","2+2"),
    #     ("3+1","3+1"),
    #     ("2+1","2+1"),
    #     ("1+1","1+1")
    #     ]
    # layout_type = CharField(
    #     max_length=4,
    #     choices=layout_list,
    #     blank=False
    # )
    primary_size = models.IntegerField(blank=False)
    secondary_size = models.IntegerField(blank=False)
    weight = models.FloatField(blank=False, default=1.0)
    quartermeister_required = models.BooleanField(default=False)   
    

    def __str__(self):
        return str(self.primary_size)+"+"+str(self.secondary_size)
    
    def get_size(self):
        """May be needed later
        """
        return self.primary_size + self.secondary_size

    def dictate(self):
        return {
            'primary_size': self.primary_size ,
            'secondary_size': self.secondary_size , 
            'quartermeister_required': self.quartermeister_required
        }


class Layout(models.Model):

    layout_type = models.ForeignKey(Slots, on_delete=models.PROTECT, blank=False, default="3+1")
    primary_type = models.ForeignKey(WeaponType, on_delete=models.PROTECT, blank=False, related_name='primary_weapon_type')
    secondary_type = models.ForeignKey(WeaponType, on_delete=models.PROTECT, blank=False, related_name='secondary_weapon_type')
    weight = models.FloatField(default=1)
    
    def __str__(self):
        return str(self.primary_type) + ' + ' + str(self.secondary_type)

    def dictate(self):
        return {
            'layout_type': self.layout_type ,
            'primary_type': self.primary_type ,
            'secondary_type': self.secondary_type ,
            'chance': self.chance ,
            'name': str(self.primary_type) + ' + ' + str(self.secondary_type) 
        }

    





