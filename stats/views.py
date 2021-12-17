from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def show_stats_table(request):
    #this is main page of the app
    response = render(request, "stats_list.html")
    return HttpResponse(response)

def sample(request):
    #this is main page of the app
    response = render(request, "sample.html")
    return HttpResponse(response)


def add_match(request):
    #this is page to add new match
    # output = render (request, "landing.html")
    return HttpResponse("whoopsie!")


def add_match_details(request):
    #this is page to add your details to existing match
    return HttpResponse("TBD!")
