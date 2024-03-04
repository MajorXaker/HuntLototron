from django.http import HttpResponse
from django.shortcuts import render

from utils.get_credentials import UserCredsOrganised


def home(request):
    user = UserCredsOrganised.from_request(request)

    output = render(request, "landing.html", {"user": user})
    return HttpResponse(output)
