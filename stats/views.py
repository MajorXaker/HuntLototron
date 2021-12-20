from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.checks import messages
from django.shortcuts import render
from django.http import HttpResponse,  HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import View
from .forms import FormAddMatch_simple
from stats.models import AmmoType, Compound, Match, Player, Map
from roulette.models import Weapon
from HuntLototron.auth_helpers import AuthShowdown
from itertools import chain
from operator import attrgetter
# Create your views here.



@login_required
def show_stats_table(request):
    user = AuthShowdown.credentials_to_dict(request)

    #we need to know whose matches are we looking for
    if user['has_aka']:
        look_for_user = Player.objects.get(also_known_as = user['playername'])
    else:
        look_for_user = User.objects.get(username = user['username']).username_of_player

    #3 queries with the name of active player
    p1_group = Match.objects.filter(player_1 = look_for_user)
    p2_group = Match.objects.filter(player_2 = look_for_user)
    p3_group = Match.objects.filter(player_3 = look_for_user)
    
    #results are sorted by their id
    result = sorted(
        chain(p1_group, p2_group, p3_group),
        key=attrgetter('id'))


    response = render(request, "stats_list.html", {'matches': result, 'user':user})
    return response

def show_match_detail(request, match_id):
    try:
        user = AuthShowdown.credentials_to_dict(request, debug=True)
        match = Match.objects.get(pk=match_id)


        if not user['credentials'] in match.players():
            print('GO AWAY')
            return render(request, "404_or_403_match.html", status=403)

        additional = {}
        additional["player_2_here"] = False if match.player_2 == 'None' else True
        additional["player_3_here"] = False if match.player_3 == 'None' else True
        # print(additional['player_2_here'])
       
        response = render(request, "detailed_stats.html", {'match': match, 'additional': additional, 'user':user})
    except Match.DoesNotExist:
        return render(request, "404_or_403_match.html", status=403)
        
    return response


class AddMatch(View):
    def get(self, request):
        user = AuthShowdown.credentials_to_dict(request)

        form = FormAddMatch_simple()
        context = {
            'form': form,
            'user': user
        }

        output = render (request, "add_match.html", context)

        return output
    
    def post(self, request):
        user = AuthShowdown.credentials_to_dict(request)
        form = FormAddMatch_simple(request.POST)
        
        if form.is_valid():

            # print('ALL DATA BEGIN')
            # print(form.cleaned_data)
            # print('ALL DATA END')

            raw_teammates = [
                form.cleaned_data['teammate_1'].split('.'),
                form.cleaned_data['teammate_2'].split('.'),
                form.cleaned_data['teammate_3'].split('.'),
            ]

            teammates = []
            for teammate in raw_teammates:

                if teammate[0] == 'a':
                    teammates.append(Player.objects.get(also_known_as = teammate[1]))
                else:
                    userclass = User.objects.get(username=teammate[1])
                    teammates.append(userclass.username_of_player) #this should return player class of this user

            match = Match(
                wl_status = form.cleaned_data['wl_status'],
                date = form.cleaned_data['date'],
                kills_total = form.cleaned_data['kills_total'],
                bounty = form.cleaned_data['bounty'],
                playtime = form.cleaned_data['playtime'],
                
                player_1 = teammates[0],
                player_2 = teammates[1],
                player_3 = teammates[2],
                map = Map.objects.get(name=form.cleaned_data['map']),
                player_1_kills = form.cleaned_data['player_kills'],
                player_1_assists = form.cleaned_data['player_assists'],
                player_1_deaths = form.cleaned_data['player_deaths'],
                player_1_primary_weapon = Weapon.objects.get(name=form.cleaned_data['primary_weapon']),
                player_1_primary_ammo_A = AmmoType.objects.get(name=form.cleaned_data['primary_ammo_A']),
                player_1_primary_ammo_B = AmmoType.objects.get(name=form.cleaned_data['primary_ammo_B']),
                player_1_secondary_weapon = Weapon.objects.get(name=form.cleaned_data['secondary_weapon']),
                player_1_secondary_ammo_A = AmmoType.objects.get(name=form.cleaned_data['secondary_ammo_A']),
                player_1_secondary_ammo_B = AmmoType.objects.get(name=form.cleaned_data['secondary_ammo_B']),
                
            ) 
            match.save()
            for name in form.cleaned_data['fight_locations']:
                match.fights_locations.add(name)
            match.save()

            return HttpResponseRedirect(reverse('stats:table') )
        else:
            print('not valid form')
            print(form.errors)
        
        
        context = {
            'form': form,
            'user': user
        }

        output = render (request, "add_match.html", context)

        return output



# @login_required
# def add_match_simple(request):
#     #this is page to add new match

#     if request.method == 'POST':
#         form = FormAddMatch_simple(request.POST)
        
#         if form.is_valid():

#             # print('ALL DATA BEGIN')
#             # print(form.cleaned_data)
#             # print('ALL DATA END')

#             raw_teammates = [
#                 form.cleaned_data['teammate_1'].split('.'),
#                 form.cleaned_data['teammate_2'].split('.'),
#                 form.cleaned_data['teammate_3'].split('.'),
#             ]

#             teammates = []
#             for teammate in raw_teammates:

#                 if teammate[0] == 'a':
#                     teammates.append(Player.objects.get(also_known_as = teammate[1]))
#                 else:
#                     userclass = User.objects.get(username=teammate[1])
#                     teammates.append(userclass.username_of_player) #this should return player class of this user

#             match = Match(
#                 wl_status = form.cleaned_data['wl_status'],
#                 date = form.cleaned_data['date'],
#                 kills_total = form.cleaned_data['kills_total'],
#                 bounty = form.cleaned_data['bounty'],
#                 playtime = form.cleaned_data['playtime'],
                
#                 player_1 = teammates[0],
#                 player_2 = teammates[1],
#                 player_3 = teammates[2],
#                 map = Map.objects.get(name=form.cleaned_data['map']),
#                 player_1_kills = form.cleaned_data['player_kills'],
#                 player_1_assists = form.cleaned_data['player_assists'],
#                 player_1_deaths = form.cleaned_data['player_deaths'],
#                 player_1_primary_weapon = Weapon.objects.get(name=form.cleaned_data['primary_weapon']),
#                 player_1_primary_ammo_A = AmmoType.objects.get(name=form.cleaned_data['primary_ammo_A']),
#                 player_1_primary_ammo_B = AmmoType.objects.get(name=form.cleaned_data['primary_ammo_B']),
#                 player_1_secondary_weapon = Weapon.objects.get(name=form.cleaned_data['secondary_weapon']),
#                 player_1_secondary_ammo_A = AmmoType.objects.get(name=form.cleaned_data['secondary_ammo_A']),
#                 player_1_secondary_ammo_B = AmmoType.objects.get(name=form.cleaned_data['secondary_ammo_B']),
                
#             ) 
#             match.save()
#             for name in form.cleaned_data['fight_locations']:
#                 match.fights_locations.add(name)
#             match.save()

#             return HttpResponseRedirect(reverse('stats:table') )
#         else:
#             print('not valid form')
#             print(form.errors)

#     else:
        
#         form = FormAddMatch_simple()

        

#     context = {
#         'form': form
#     }

#     output = render (request, "add_match.html", context)





#     return output


def sample(request):
    #this is main page of the app
    data = {'data' : ''}



    
    response = render(request, "sample.html", data)
    return HttpResponse(response)


def profile(request):
    pass

# def add_match_detailed(request):
    
#     #this is page to add your details to existing match
#     return HttpResponse("TBD!")
