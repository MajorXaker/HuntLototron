from django.contrib.auth.decorators import login_required
from django.urls import path, include

import stats.views.add_match
import stats.views.edit_match
import stats.views.match_details
import stats.views.matches_table
import stats.views.sample
from . import views

# movies/
# movies/1/details

app_name = "stats"
# нужно чтобы делать линки вот такого типа "movies:detail" в хтмл разметке, типо такого {% url 'match:details' match.id %}

urlpatterns = [
    path("", stats.views.matches_table.show_stats_table, name="table"),
    path("<int:match_id>", stats.views.match_details.show_match_detail, name="match_details"),
    path("edit/<int:match_id>", stats.views.edit_match.EditMatch.as_view(), name="edit"),
    path("add", stats.views.add_match.AddMatch.as_view(), name="add"),
    path("sample", stats.views.sample.sample, name="add_details"),
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
