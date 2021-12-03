from django.shortcuts import render
from django.http import HttpResponse
from .models import Weapon

# Create your views here.

def index(request):
    # return HttpResponse("General Kenobi")
    guns = Weapon.objects.all()

    output = render (request, "index.html", {'weapons': guns})



    return HttpResponse(output)