from django.shortcuts import render
from django.http import HttpResponse
from HuntLototron.auth_helpers import AuthShowdown

# Create your views here.

def home(request):
    user = AuthShowdown.credentials_to_dict(request, debug=True)

    output = render (request, "landing.html", {"user":user})
    return HttpResponse(output)

def profile(request):

    return HttpResponse("lalala")