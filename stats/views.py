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
        match = Match.objects.get(pk=match_id)
        user = AuxClass.credentials_to_dict(request)

        open_for_browsing = (
            request.user.is_staff,
            request.user.username_of_player in match.players(is_class = True),
            match.display_allowed()
        ) # one TRUE result lets us to see the match

        if not request.user.username_of_player in match.players(is_class = True):
            match.set_encoding()
           

        additional = {}
        additional["player_2_here"] = False if str(type(match.player_2)) == "<class 'NoneType'>" else True
        additional["player_3_here"] = False if str(type(match.player_3)) == "<class 'NoneType'>" else True
        
        
        

        # temporary placeholder, as bounty for now is only 4 match, not for person
        # additional['player_1_bounty'] =  match.bounty
        # additional['player_2_bounty'] =  match.bounty
        # additional['player_3_bounty'] =  match.bounty
        
       
        if True in open_for_browsing:
            response = render(request, "detailed_stats.html", {'match': match, 'additional': additional, 'user':user})
        else:
            response = render(request, "404_or_403_match.html", status=403)
        
        return response
    except Match.DoesNotExist:
        return render(request, "404_or_403_match.html", status=403)
        
    


class AddMatch(View):
    def get(self, request):
        user = AuxClass.credentials_to_dict(request)

        initial_data = {
            'player_1': request.user.username_of_player,
            
        }

        form = MatchAddForm(initial=initial_data)

        context = {
            'form': form,
            'user': user,
            
        }

        output = render (request, "add_match.html", context)

        return output
    
    def post(self, request):
        user = AuxClass.credentials_to_dict(request)
        form = MatchAddForm(request.POST)

        
        if form.is_valid():

            
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
            
            print(f'In match player 1 m weapon is {match_on_table.player_1_primary_weapon}, its size is {match_on_table.player_1_primary_weapon.size}')

            print(match_on_table.verify_guns(user['position'])[0])
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
    user = AuxClass.credentials_to_dict(request)

    # aaa = Player.objects.get(also_known_as = "None")
    em = Match.objects.get(pk = 12)
    mathes_hashed = [match.get_md5() for match in Match.objects.all()]

    print(mathes_hashed)

    context = {

            'user': user
        }
        
    # print(request.GET.keys())

    
    response = render(request, "sample.html", context)
    return HttpResponse(response)

