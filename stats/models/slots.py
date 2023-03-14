from django.db import models


class Slots(models.Model):
    primary_size = models.IntegerField(blank=False)
    secondary_size = models.IntegerField(blank=False)
    weight = models.FloatField(blank=False, default=1.0)
    quartermeister_required = models.BooleanField(default=False)

    def __str__(self):
        return str(self.primary_size) + "+" + str(self.secondary_size)

    def get_size(self):
        """May be needed later"""
        return self.primary_size + self.secondary_size

    def dictate(self):
        return {
            "primary_size": self.primary_size,
            "secondary_size": self.secondary_size,
            "quartermeister_required": self.quartermeister_required,
        }
