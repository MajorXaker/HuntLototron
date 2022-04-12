from django.db import models

from stats.models.map import Map


class Compound(models.Model):
    name = models.CharField(primary_key=True, max_length=80)
    from_map = models.ForeignKey(Map, verbose_name="Map", on_delete=models.PROTECT, default=None)
    double_clue = models.BooleanField()
    # IDK why I may need these, but I create it for later
    # atm these values are used in JS, still I doubt that it's a good idea to pull them every time from DB
    # yet if I need to correct them I'll just correct values in db
    # it will require wiring frontend js to db
    x_relative = models.FloatField(default=-2)
    y_relative = models.FloatField(default=-2)

    def __str__(self) -> str:
        return self.name
