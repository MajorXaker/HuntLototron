from django.contrib import admin

from .models import Player, Compound, Map, Match, AmmoType

# Register your models here.

class Match_admin(admin.ModelAdmin):
    list_display = ("id",'date','wl_status', 'player_1' , 'player_2', 'player_3')


class Compound_admin(admin.ModelAdmin):
    list_display = ("name", "from_map")

class Player_Admin(admin.ModelAdmin):
    list_display = ('username', 'also_known_as')


admin.site.register(Player, Player_Admin)
admin.site.register(Match, Match_admin)
admin.site.register(Map)
admin.site.register(Compound, Compound_admin)
admin.site.register(AmmoType)
# admin.site.register(Kit) # RIP KIT, u wont be forgotten
