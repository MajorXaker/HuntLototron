from django.contrib import admin
from django.db.models.base import Model
from .models import WeaponType, Weapon, Layout, Slots

# Register your models here.

class WeaponType_admin(admin.ModelAdmin):
    # list_display = ("name", "translated_title")
    exclude = ("translated_title",'core_gun','size', 'sights' , 'melee','muzzle' ,'weight','price')

class Layout_admin(admin.ModelAdmin):
    list_display = ("primary_type", "secondary_type", "layout_type",)


admin.site.register(WeaponType, WeaponType_admin)
admin.site.register(Weapon)
admin.site.register(Layout, Layout_admin)
admin.site.register(Slots)