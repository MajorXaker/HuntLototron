from django.urls import path
from . import views

# movies/
# movies/1/details

app_name = "stats"
#нужно чтобы делать линки вот такого типа "movies:detail" в хтмл разметке

urlpatterns = [
    path('', views.show_stats_table, name = "table"),
    path('add', views.add_match, name = "add"),
    path('add_details', views.add_match_details, name = "add_details"),
    path('sample', views.sample, name = "add_details"),


]