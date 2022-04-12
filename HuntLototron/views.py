from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic.base import View

from django.contrib.auth.mixins import LoginRequiredMixin
from HuntLototron.auxilary import AuxClass, MatchesDecoder
from itertools import chain
from operator import attrgetter
from .forms import RedeemHashInvite, RegistrationFormA, UserSettingsForm, CreateHashInvite, CSVUploadForm
import csv



# from HuntLototron.base_constructs import ViewBaseConstruct
# try to use base base constructs of views, so reducing a need to duplicate code

# Create your views here.



def home(request):
    user = AuxClass.credentials_to_dict(request)

    # output = render (request, "landing.html") #temporary! delete
    output = render (request, "landing.html", {"user":user})
    return HttpResponse(output)

class ProfilePage(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'

    
    def get(self, request):
        user = AuxClass.credentials_to_dict(request)

        csv_form = CSVUploadForm()

        additional = {}
        context = {
                'user': user,
                'additional': additional,
                'csv_form': csv_form
            }


        return render (request, "registration/profile.html", context)


    
    def post(self, request):
        user = AuxClass.credentials_to_dict(request)
        csv_form = CSVUploadForm(request.POST, request.FILES)
        player = request.user.username_of_player

        if csv_form.is_valid():
            print('Form valid')
            filename = request.FILES['file'].name
            file_as_text  = open(filename, "r")
            
            decoder = MatchesDecoder(file_as_text, player)

            decoder.normalise()

            
            
            decoder.transfer()
            
            response = HttpResponse(
                content_type='text/txt',
                headers={'Content-Disposition': 'attachment; filename="log.txt"'},
            )
            for message in decoder.messages:
                response.write(message)
                response.write('\n')
                response.write('----')
                response.write('\n')
            return response
            
            # with open("log.txt", 'wt') as file:
            #     for message in messages:
            #         file.write(message)

        else:
            print('Form invalid')
            print(csv_form.errors)

        additional = {}
        context = {
            'user': user,
            'additional': additional,
            'csv_form': csv_form
        }

        return render(request, "registration/profile.html", context)

class RegistrationPage(View):

    def get(self, request):
        form = RegistrationFormA()

        context = {
            'form': form,
        }

        output = render (request, "registration/registration.html", context)

        return output
    

    def post(self, request):
        form = RegistrationFormA(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()

            player = Player()
            player.update(user)
            player.save()

            # current_site = get_current_site(request)
            # subject = 'Activate Your MySite Account'
            # message = render_to_string('account_activation_email.html', {
            #     'user': user,
            #     'domain': current_site.domain,
            #     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            #     'token': account_activation_token.make_token(user),
            # })
            # user.email_user(subject, message)
            login(request, user)
            return redirect('profile')
            # return redirect('account_activation_sent') #for now activation is disabled

        else:
            form = RegistrationFormA(request.POST)
            context = {
            'form': form,
            }
            output = render (request, "registration/registration.html", context)
            return output

def HashDelete(request, hash_key):

    hashed_player = Player.objects.get(hash_key = hash_key)

    # look if this player participated in any matches
    matches_p1 = Match.objects.filter(player_1 = hashed_player)
    matches_p2 = Match.objects.filter(player_2 = hashed_player)
    matches_p3 = Match.objects.filter(player_3 = hashed_player)

    matches_as_list = sorted(
        chain(matches_p1, matches_p2, matches_p3),
        key=attrgetter('id'))

    if len(matches_as_list) > 0:
        # do smth if mathes are found TBD
        # for example change with unknown player
        
        unknown_player = get(username='UnknownHunter').username_of_player
        for match in matches_as_list:
            match.swap_players(hashed_player, unknown_player)
        hashed_player.delete()
        return redirect('profile_settings', permanent=True)
    else:
        # delete this hash if mathes are not found
        hashed_player.delete()
        return redirect('profile_settings', permanent=True)


def export_Matches(request):
     # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="matches.csv"'},
    )
 
    player = request.user.username_of_player

    #3 queries with the name of active player
    p1_group = Match.objects.filter(player_1 = player)
    p2_group = Match.objects.filter(player_2 = player)
    p3_group = Match.objects.filter(player_3 = player)
    
    #results are sorted by their id
    result_as_list = sorted(
        chain(p1_group, p2_group, p3_group),
        key=attrgetter('id'))

    model_fields_names = []
    fields = Match._meta.get_fields()
    for field in fields:
        field_data = field.name
        model_fields_names.append(field_data)

    writer = csv.writer(response)
    writer.writerow(model_fields_names)


    for match in result_as_list:
        fields = match._meta.get_fields()
        pure_values = []
        for field in fields:
            if field.many_to_one:
                # decodes foreing field relation, as value to string returns only an ID
                id = field.value_to_string(match)
                try:
                    a_value = field.related_model.objects.get(pk=id)
                except (ValueError):
                    a_value = 'None'
                except Map.DoesNotExist:
                    a_value = 'Undefined'
            elif field.many_to_many:
                a_value = '+'.join([item.name for item in field.value_from_object(match)])  
            else:
                a_value = field.value_to_string(match)
            pure_values.append(a_value)
        writer.writerow(pure_values)



    return response

class ProfileSettings(View):

    def get(self, request):
        user = AuxClass.credentials_to_dict(request)
        player = get(username = user['username']).username_of_player
        
        active_user = user['user']
        active_user_invited = Player.objects.filter(created_by = active_user)

        form_create_hash = CreateHashInvite()
        form_redeem_invite = RedeemHashInvite()
        form_settings = UserSettingsForm(instance=player)
        
        context = {
            'user':user,
            'form_settings':form_settings,
            'form_invites':form_create_hash,
            'form_redeem': form_redeem_invite,
            'invites':active_user_invited,
        }
        return render(request, 'registration/profile_settings.html', context)


    def post(self, request):
        user = AuxClass.credentials_to_dict(request)
        additional = {} #dict for sending strings to front

        active_user = user['user']
        active_user_invited = Player.objects.filter(created_by = active_user)

        form_create_hash = CreateHashInvite(request.POST)
        form_redeem_invite = RedeemHashInvite(request.POST)
        form_settings = UserSettingsForm(request.POST)

        if 'settings_update' in request.POST.keys():
            user = AuxClass.credentials_to_dict(request)

            player = get(username = user['username']).username_of_player

            
            
            if form_settings.is_valid():
                player.also_known_as = form_settings.cleaned_data['also_known_as']
                player.allow_see_mathes = form_settings.cleaned_data['allow_see_mathes']        
                player.allow_see_name = form_settings.cleaned_data['allow_see_name']                
                player.show_only_my_matches = form_settings.cleaned_data['show_only_my_matches']
                player.use_alternative_name = True

                player.save()

            
                user['name'] = form_settings.cleaned_data['also_known_as']

            additional = {'changed':True}
            

        


        if 'hash_create' in request.POST.keys():
            if form_create_hash.is_valid():
                new_player_name = form_create_hash.cleaned_data['player_name']
                hash_invite = AuxClass.encode_md5(new_player_name, user['name'])

                player_invited = Player()
                player_invited.hash_key = hash_invite
                player_invited.created_by = request.user # now you have no limits on the amounts of invites
                # TODO implement limits
                player_invited.also_known_as = new_player_name
                player_invited.hash_redeemable = True
                player_invited.use_alternative_name = True
                player_invited.save()
                form_create_hash = CreateHashInvite()

                
        elif 'hash_redeem' in request.POST.keys():
            
            if form_redeem_invite.is_valid():
                
                hashed_player = Player.objects.get(hash_key = form_redeem_invite.cleaned_data['hash_key'])

                if hashed_player.created_by == active_user:
                    
                    form_redeem_invite = RedeemHashInvite()
                    additional['is_redeem_message'] = True
                    
                    additional['redeem_message'] = f'You cannot redeem your own hash-invite.'
                else:
                    matches_with_hashed_player_as_1 = Match.objects.filter(player_1 = hashed_player)
                    matches_with_hashed_player_as_2 = Match.objects.filter(player_2 = hashed_player)
                    matches_with_hashed_player_as_3 = Match.objects.filter(player_3 = hashed_player)
                    matches_with_hashed_player = list(chain(matches_with_hashed_player_as_1, matches_with_hashed_player_as_2, matches_with_hashed_player_as_3))
                    
                    try:
                        [match.swap_players(hashed_player, active_user.username_of_player) for match in matches_with_hashed_player]
                    except Match.PlayerDuplicationError:
                        additional['is_redeem_message'] = True
                        additional['redeem_message'] = f'Redeeming this hash-invite would lead to player duplication in match. Redeem denied.'
                    else: 
                        [match.save() for match in matches_with_hashed_player]
                        hashed_player.delete()
                        additional['is_redeem_message'] = True
                        additional['redeem_message'] = 'Hash-invite has been redeemed.'
                        form_redeem_invite = RedeemHashInvite()
            else:
                additional['is_redeem_message'] = True
                additional['redeem_message'] = 'Hash invite is not found or already redeemed.'
                form_redeem_invite = RedeemHashInvite()



                    
        context = {
            'user':user,
            'form_invites':form_create_hash,
            'form_settings':form_settings,
            'invites':active_user_invited,
            'form_redeem': form_redeem_invite,
            'additional':additional
        }

        # return render (request, "registration/profile.html", context)
        return render(request, 'registration/profile_settings.html', context)




# def account_activation_sent(request):
#     return render(request, 'account_activation_sent.html')

# def activate(request, uidb64, token):
#     try:
#         uid = force_text(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None

#     if user is not None and account_activation_token.check_token(user, token):
#         user.is_active = True
#         user.profile.email_confirmed = True
#         user.save()
#         login(request, user)
#         return redirect('home')
#     else:
#         return render(request, 'account_activation_invalid.html')
