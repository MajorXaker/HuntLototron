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
        
        if request.user.username_of_player.show_only_my_matches:
            filtered_matches = []
        else:
            #other matches group
            all_matches = Match.objects.all()
            filtered_matches = [match for match in all_matches if match.display_allowed()]
            hashed_matches = [match.set_encoding() for match in filtered_matches]

        #results are sorted by their id
        result_as_list = sorted(
            chain(p1_group, p2_group, p3_group, filtered_matches),
            key=attrgetter('id'))

        result_as_set = set(result_as_list)
        result_ready = list(result_as_set)
        result_ready.reverse()



    else:
        result_ready = Match.objects.all()


    response = render(request, "stats_list.html", {'matches': result_ready, 'user':user})
    return response

def show_match_detail(request, match_id):
    try:
        user = AuxClass.credentials_to_dict(request)
        match = Match.objects.get(pk=match_id)

        open_for_browsing = (
            request.user.is_staff,
            request.user.username_of_player in match.players(is_class = True),
            match.display_allowed()
        ) # one TRUE result lets us to see the match

        if not request.user.username_of_player in match.players(is_class = True):
            match.set_encoding()
           

        additional = {}
        additional["player_2_here"] = False if match.player_2 == 'None' else True
        additional["player_3_here"] = False if match.player_3 == 'None' else True
        
       
        if True in open_for_browsing:
            response = render(request, "detailed_stats.html", {'match': match, 'additional': additional, 'user':user})
        else:
            response = render(request, "404_or_403_match.html", status=403)
        
        return response
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

            print(form.player_1_signature)
            form.save()
           
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
    
    # common_fields = ['id_date', 'id_wl_status', 'id_player_1', 'id_player_2', 'id_player_3', 'id_bounty', 'id_playtime', 'id_kills_total', 'id_fights_locations']
    # player_fields = ['null']
    # for player in range(3):
    #     fields = ['kills', 'assists', 'deaths', 'primary_weapon', 'secondary_weapon', 'primary_ammo_A', 'primary_ammo_B', 'secondary_ammo_A', 'secondary_ammo_B']
    #     commands_for_player = []
        
    #     for command in fields:
    #         full_command = 'id_player_' + str(player) + '_' + command
    #         commands_for_player.append(full_command)
        
    #     player_fields.append(commands_for_player)
    



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
        
    print(request.GET.keys())

    
    response = render(request, "sample.html", data)
    return HttpResponse(response)

