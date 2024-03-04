from django.http import HttpResponse
from django.shortcuts import render

from stats import models as m
from utils.get_credentials import UserCredsOrganised


def sample(request):
    # this is main page of the app
    user = UserCredsOrganised.from_request(request)

    # aaa = Player.objects.get(also_known_as = "None")
    em = m.Match.objects.get(pk=12)
    mathes_hashed = [match.get_md5() for match in m.Match.objects.all()]

    print(mathes_hashed)

    context = {"user": user}

    # print(request.GET.keys())

    response = render(request, "sample.html", context)
    return HttpResponse(response)
