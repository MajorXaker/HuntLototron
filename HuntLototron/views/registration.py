from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.views import View

from HuntLototron.forms import RegistrationFormA
from stats.models import Player


class RegistrationPage(View):
    def get(self, request):
        form = RegistrationFormA()

        context = {
            "form": form,
        }

        output = render(request, "registration/registration.html", context)

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
            return redirect("profile")
            # return redirect('account_activation_sent') #for now activation is disabled

        else:
            form = RegistrationFormA(request.POST)
            context = {
                "form": form,
            }
            output = render(request, "registration/registration.html", context)
            return output
