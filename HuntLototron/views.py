from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic.base import View
from stats.models import Match, Player
from django.contrib.auth.mixins import LoginRequiredMixin
from HuntLototron.auxilary import AuxClass
from itertools import chain
from operator import attrgetter
from .forms import RedeemHashInvite, RegistrationFormA, UserSettingsForm, CreateHashInvite


from HuntLototron.base_constructs import ViewBaseConstruct
# try to use base base constructs of views, so reducing a need to duplicate code

# Create your views here.



def home(request):
    user = AuxClass.credentials_to_dict(request)

    output = render (request, "landing.html", {"user":user})
    return HttpResponse(output)

class ProfilePage(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'

    
    def get(self, request):
        user = AuxClass.credentials_to_dict(request)

        player = User.objects.get(username = user['username']).username_of_player

        form = UserSettingsForm(instance=player)

        additional = {}
        context = {
                'user': user,
                'form': form,
                'additional':additional
            }


        return render (request, "registration/profile.html", context)


    
    def post(self, request):
        user = AuxClass.credentials_to_dict(request)

        player = User.objects.get(username = user['username']).username_of_player

        form = UserSettingsForm(request.POST)
        
        if form.is_valid():
            player.also_known_as = form.cleaned_data['also_known_as']
            player.allow_see_mathes = form.cleaned_data['allow_see_mathes']        
            player.allow_see_name = form.cleaned_data['allow_see_name']                
            player.show_only_my_matches = form.cleaned_data['show_only_my_matches']
            player.use_alternative_name = True

            player.save()

        
            user['name'] = form.cleaned_data['also_known_as']

        additional = {'changed':True}
        
        context = {
                'user': user,
                'form': form,
                'additional':additional
            }


        return render (request, "registration/profile.html", context)


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

class ProfileSettings(View):
    # now only logic for hash creation
    # later POST should distinguish between two-three submit buttons: hash create \ hash redeem \ settings update
    def get(self, request):
        user = AuxClass.credentials_to_dict(request)

        
        active_user = user['user']
        active_user_invited = Player.objects.filter(created_by = active_user)

        form_create_hash = CreateHashInvite()
        form_redeem_invite = RedeemHashInvite()
        
        context = {
            'user':user,
            'form_invites':form_create_hash,
            'invites':active_user_invited,
            'form_redeem': form_redeem_invite
        }
        return render(request, 'registration/profile_settings.html', context)


    def post(self, request):
        user = AuxClass.credentials_to_dict(request)
        additional = {} #dict for sending strings to front

        active_user = user['user']
        active_user_invited = Player.objects.filter(created_by = active_user)

        form_create_hash = CreateHashInvite(request.POST)
        form_redeem_invite = RedeemHashInvite(request.POST)

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
            'invites':active_user_invited,
            'form_redeem': form_redeem_invite,
            'additional':additional
        }
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
