from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.checks import messages
from django.shortcuts import render
from django.http import HttpResponse,  HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import View
# from .forms import FormAddMatch_simple
from .forms import MatchAddForm, MatchEditForm
from stats.models import AmmoType, Compound, Match, Player, Map
from roulette.models import Weapon
from HuntLototron.auxilary import AuxClass
from itertools import chain
from operator import attrgetter
# Create your views here.



@login_required
def show_stats_table(request):
    user = AuxClass.credentials_to_dict(request)

    if not request.user.is_staff:
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
    else:
        result = Match.objects.all()


    response = render(request, "stats_list.html", {'matches': result, 'user':user})
    return response

def show_match_detail(request, match_id):
    try:
        user = AuxClass.credentials_to_dict(request)
        match = Match.objects.get(pk=match_id)

        if not request.user.is_staff:
            if not user['credentials'] in match.players():

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
        user = AuxClass.credentials_to_dict(request)

        initial_data = {
            'teammate_1': request.user.username_of_player.service_name(),
            
        }

        # form = FormAddMatch_simple(initial=initial_data)
        form = MatchAddForm(initial=initial_data)

        context = {
            'form': form,
            'user': user,
            
        }

        output = render (request, "add_match.html", context)

        return output
    
    def post(self, request):
        user = AuxClass.credentials_to_dict(request)
        # form = FormAddMatch_simple(request.POST)
        form = MatchAddForm(request.POST)

        
        if form.is_valid():

            # print('ALL DATA BEGIN')
            # print(form.cleaned_data)
            # print('ALL DATA END')

            # raw_teammates = [
            #     form.cleaned_data['teammate_1'].split('.'),
            #     form.cleaned_data['teammate_2'].split('.'),
            #     form.cleaned_data['teammate_3'].split('.'),
            # ]

            # teammates = []
            # for teammate in raw_teammates:

            #     if teammate[0] == 'a':
            #         teammates.append(Player.objects.get(also_known_as = teammate[1]))
            #     else:
            #         userclass = User.objects.get(username=teammate[1])
            #         teammates.append(userclass.username_of_player) #this should return player class of this user

            # match = Match(
            #     wl_status = form.cleaned_data['wl_status'],
            #     date = form.cleaned_data['date'],
            #     kills_total = form.cleaned_data['kills_total'],
            #     bounty = form.cleaned_data['bounty'],
            #     playtime = form.cleaned_data['playtime'],
                
            #     player_1 = teammates[0],
            #     player_2 = teammates[1],
            #     player_3 = teammates[2],
            #     map = Map.objects.get(name=form.cleaned_data['map']),
            #     player_1_kills = form.cleaned_data['player_1_kills'],
            #     player_1_assists = form.cleaned_data['player_1_assists'],
            #     player_1_deaths = form.cleaned_data['player_1_deaths'],
            #     player_1_primary_weapon = Weapon.objects.get(name=form.cleaned_data['player_1_primary_weapon']),
            #     player_1_primary_ammo_A = AmmoType.objects.get(name=form.cleaned_data['player_1_primary_ammo_A']),
            #     player_1_primary_ammo_B = AmmoType.objects.get(name=form.cleaned_data['player_1_primary_ammo_B']),
            #     player_1_secondary_weapon = Weapon.objects.get(name=form.cleaned_data['player_1_secondary_weapon']),
            #     player_1_secondary_ammo_A = AmmoType.objects.get(name=form.cleaned_data['player_1_secondary_ammo_A']),
            #     player_1_secondary_ammo_B = AmmoType.objects.get(name=form.cleaned_data['player_1_secondary_ammo_B']),
                
            # ) 
            form.save()
            # for name in form.cleaned_data['fight_locations']:
            #     match.fights_locations.add(name)
            # match.save()

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

class EditMatch(View):
    
    common_fields = ['id_date', 'id_wl_status', 'id_player_1', 'id_player_2', 'id_player_3', 'id_bounty', 'id_playtime', 'id_kills_total', 'id_fights_locations']
    player_fields = ['null']
    for player in range(3):
        fields = ['kills', 'assists', 'deaths', 'primary_weapon', 'secondary_weapon', 'primary_ammo_A', 'primary_ammo_B', 'secondary_ammo_A', 'secondary_ammo_B']
        commands_for_player = []
        
        for command in fields:
            full_command = 'id_player_' + str(player) + '_' + command
            commands_for_player.append(full_command)
        
        player_fields.append(commands_for_player)
    



    def get(self, request, match_id):
        user = AuxClass.credentials_to_dict(request)

        match_on_table = Match.objects.get(pk=match_id)
        form = MatchEditForm(instance=match_on_table)
        user['position'] = match_on_table.get_player_slot(user['credentials'])
        if user['position'] == 0 and request.user.is_staff == False:
            return render(request, "404_or_403_match.html", status=403)

        context = {
            'form': form,
            'user': user,
            
        }

        output = render (request, "edit_match.html", context)

        return output
    
    def post(self, request, match_id):
        user = AuxClass.credentials_to_dict(request)
        form = MatchEditForm(request.POST,)

        match_on_table = Match.objects.get(pk=match_id)
        user['position'] = match_on_table.get_player_slot(user['credentials'])
        
        if form.is_valid():
            
            form.save()

            return HttpResponseRedirect(reverse('stats:table') )
        
            
        
        context = {
            'form': form,
            'user': user
        }

        output = render (request, "edit_match.html", context)

        return output
    






def sample(request):
    #this is main page of the app
    data = {'data' : ''}



    
    response = render(request, "sample.html", data)
    return HttpResponse(response)


def profile(request):
    pass
