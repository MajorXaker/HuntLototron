from django.urls import path
from . import views

# movies/
# movies/1/details

app_name = "roulette"
#нужно чтобы делать линки вот такого типа "movies:detail" в хтмл разметке

urlpatterns = [
    path('', views.index, name = "index"),

]