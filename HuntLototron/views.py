from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):

    output = render (request, "landing.html")
    return HttpResponse(output)