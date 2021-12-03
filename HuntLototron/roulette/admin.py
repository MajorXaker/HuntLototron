from django.contrib import admin
from .models import WeaponType, Weapon

# Register your models here.


admin.site.register(WeaponType)
admin.site.register(Weapon)
