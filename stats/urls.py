from django.contrib.auth.decorators import login_required
from django.urls import path, include
from . import views

# movies/
# movies/1/details

app_name = "stats"
# нужно чтобы делать линки вот такого типа "movies:detail" в хтмл разметке, типо такого {% url 'match:details' match.id %}

urlpatterns = [
    path("", views.show_stats_table, name="table"),
    path("<int:match_id>", views.show_match_detail, name="match_details"),
    path("edit/<int:match_id>", views.EditMatch.as_view(), name="edit"),
    path("add", views.AddMatch.as_view(), name="add"),
    path("sample", views.sample, name="add_details"),
    # path('', login_required(ShowStats.as_view(template_name="secret.html")), name = "table"),
]
# accounts/ login/ [name='login']
# accounts/ logout/ [name='logout']
# accounts/ password_change/ [name='password_change']
# accounts/ password_change/done/ [name='password_change_done']
# accounts/ password_reset/ [name='password_reset']
# accounts/ password_reset/done/ [name='password_reset_done']
# accounts/ reset/<uidb64>/<token>/ [name='password_reset_confirm']
# accounts/ reset/done/ [name='password_reset_complete']
