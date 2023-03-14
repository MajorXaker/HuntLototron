from django.db import models


class WeaponType(models.Model):
    name = models.CharField(
        max_length=255
    )  # making a class for a weapon type, to use it later

    def __str__(self):
        return self.name
