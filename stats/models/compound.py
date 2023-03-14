from django.db import models

from .map import Map


class Compound(models.Model):
    name = models.CharField(
        primary_key=True,
        max_length=80,
    )
    from_map = models.ForeignKey(
        Map,
        verbose_name="Map",
        on_delete=models.PROTECT,
        default=None,
    )
    double_clue = models.BooleanField()
    # idk why i may need theese, but i create it for later
    # atm these values are used in JS, stil i doubt that it's a good idea to pull them every time from DB
    # yet if i need to correct them i'll just correct values in db
    # it will require wiring frontend js to db
    x_relative = models.FloatField(default=-2)
    y_relative = models.FloatField(default=-2)

    def __str__(self) -> str:
        return self.name
