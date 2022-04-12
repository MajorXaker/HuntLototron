from django.db import models


class Map(models.Model):
    name = models.CharField(primary_key=True, max_length=80)

    def __str__(self) -> str:
        return self.name