from django import forms

class add_match(forms.Form):
    date = forms.DateField( required=True)
    win = forms.BooleanField( required=False)
    loss = forms.BooleanField( required=False)

    teammate_2 = forms.CharField( max_length=80, required=False)
    teammate_3 = forms.CharField( max_length=80, required=False)

    bounty = forms.IntegerField()
    duration = forms.DurationField(required=False)

    total_kills = forms.IntegerField( required=False)

    player_1_kills = forms.IntegerField( required=False)
    player_1_assists = forms.IntegerField( required=False)
    player_1_deaths = forms.IntegerField( required=False)

    #fight_locations = 