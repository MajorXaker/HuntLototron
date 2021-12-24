from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic.base import View
from stats.models import Player
from django.contrib.auth.mixins import LoginRequiredMixin
from HuntLototron.auxilary import AuxClass

from .forms import RegistrationFormA, UserSettingsForm
from .tokens import account_activation_token

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
