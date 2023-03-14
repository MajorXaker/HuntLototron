from django.db import models


class AmmoType(models.Model):
    name = models.CharField(max_length=50, blank=False)

    def __str__(self) -> str:
        return self.name
