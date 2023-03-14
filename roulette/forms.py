from django import forms


class RouletteForm(forms.Form):
    # quartermeister = forms.BooleanField()
    pass


class SampleForm(forms.Form):
    quart = forms.CharField(label="quarty3", max_length=20)
    rolling = forms.CharField(label="rolling", max_length=20)
