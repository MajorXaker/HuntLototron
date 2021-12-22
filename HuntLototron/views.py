from django.shortcuts import render
from django.http import HttpResponse
from HuntLototron.auxilary import AuxClass

# Create your views here.

def home(request):
    user = AuxClass.credentials_to_dict(request)

    output = render (request, "landing.html", {"user":user})
    return HttpResponse(output)

def profile(request):

    return HttpResponse("lalala")