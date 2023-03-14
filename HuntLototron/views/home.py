from django.http import HttpResponse
from django.shortcuts import render

from HuntLototron.auxilary import AuxClass


def home(request):
    user = AuxClass.credentials_to_dict(request)

    # output = render (request, "landing.html") #temporary! delete
    output = render(request, "landing.html", {"user": user})
    return HttpResponse(output)
