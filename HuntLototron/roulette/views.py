from django.shortcuts import render
from django.http import HttpResponse, response
import django.core.exceptions
from .logic_core import RouletteCore
from .models import Slots, Weapon, Layout
# from .forms import SampleForm
# from .logic_core import RouletteCore

# Create your views here.

def index(request):
    # return HttpResponse("General Kenobi")    
    controls = {
        'total_roll' : "roll" in request.GET.keys(),
        'primary_roll' : "main roll" in request.GET.keys(),
        'secondary_roll' : "secondary roll" in request.GET.keys(),
        'quartermaster' : "quartermaster" in request.GET.keys()
    }


    previous_primary = request.COOKIES.get('previous_primary')
    previous_secondary = request.COOKIES.get('previous_secondary')

    if previous_primary == None or previous_secondary == None:
        primary_weapon = "Hit Roll Button"
        secondary_weapon = "Hit Roll Button"   
    else:
        primary_weapon = previous_primary
        secondary_weapon = previous_secondary
    

    if controls["total_roll"]:
        loadout = RouletteCore().create_final_loadout(controls["quartermaster"])
        primary_weapon = loadout[0].name
        secondary_weapon = loadout[1].name


    elif controls["primary_roll"]:
        try:
            type_to_reroll = Weapon.objects.get(name=primary_weapon).weapon_type
            size_to_reroll = Weapon.objects.get(name=primary_weapon).size
        except Weapon.DoesNotExist:
            primary_weapon = "Get Dual Dolch, cowboy!"
        else:
            primary_weapon = RouletteCore().choose_weapon(type_to_reroll, size_to_reroll)

    elif controls["secondary_roll"]:
        try:
            type_to_reroll = Weapon.objects.get(name=secondary_weapon).weapon_type
            size_to_reroll = Weapon.objects.get(name=secondary_weapon).size
        except Weapon.DoesNotExist:
            secondary_weapon = "Get Dual Dolch, cowboy!"
        else:
            secondary_weapon = RouletteCore().choose_weapon(type_to_reroll, size_to_reroll)

    data = {
        "primary_weapon" : primary_weapon,
        "secondary_weapon" : secondary_weapon,
    }

        

    output_data = render (request, "index.html", {"data":data})
    response = HttpResponse(output_data)
    response.set_cookie('previous_primary', primary_weapon)
    response.set_cookie('previous_secondary', secondary_weapon)
    

    return response