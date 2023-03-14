import random

from stats import models as m


class RouletteCore:
    def __init__(self) -> None:
        pass

    def choose_slot(self, quart=False):
        """Gets all slot sizes from db and rolls an appropriate

        Parameters
        ---
        quart : bool
            is quartermeister present

        Returns
        ---
            Slot class for use

        """
        if quart:  # here we have hardcoded logic, if u have quartermaster u get 3+2
            # TODO quartermeister returns also slots 2+2 and 3+1 but with relative weight penalties
            slot_type = m.Slots.objects.get(quartermeister_required=True)
        else:
            applicable_slots = m.Slots.objects.filter(quartermeister_required=False)
            weights = [slot.weight for slot in applicable_slots]
            slot_type = random.choices(applicable_slots, weights=weights, k=1)[0]
        return slot_type

    def choose_layout(self, slot):
        """Gets filtered layouts  from db and rolls an appropriate

        Parameters
        ---
        slot : slot class (i.e. from .choose_slot() function)
            what size of a loadout are we searching for

        Returns
        ---
            layout class for use
        """
        applicable_layouts = m.Layout.objects.filter(layout_type=slot)
        weights = [layout.weight for layout in applicable_layouts]
        return random.choices(applicable_layouts, weights=weights, k=1)[0]

    def choose_weapon(self, weapon_type, size):
        """Gets filtered guns  from db and rolls an appropriate

        Parameters
        ---
        weapon_type : slot class (i.e. from .choose_layout() function)
            what kind of a weapon are we are searching for

        size : int
            what size of a weapon are we are searching for

        Returns
        ---
            weapon class for use
        """
        applicable_weapons = m.Weapon.objects.filter(weapon_type=weapon_type, size=size)
        weights = [weapon.weight for weapon in applicable_weapons]
        return random.choices(applicable_weapons, weights=weights, k=1)[0]

    def create_final_loadout(self, quart):
        """Creates a loadout with primary and secondary gun. Core function of a class

        Parameters
        ---
        quart : bool
            is quartermeister present

        Returns
        ---
            a tuple of 2 weapon classes for use
        """
        slot_type = self.choose_slot(quart)
        layout_type = self.choose_layout(slot_type)

        primary_weapon = self.choose_weapon(
            layout_type.primary_type, slot_type.primary_size
        )
        secondary_weapon = self.choose_weapon(
            layout_type.secondary_type, slot_type.secondary_size
        )

        return primary_weapon, secondary_weapon
