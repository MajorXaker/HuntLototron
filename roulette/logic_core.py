import csv
import random

from .models import Weapon, Slots, Layout, WeaponType


class RouletteCore():

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
        if quart: #here we have hardcoded logic, if u have quartermaster u get 3+2
            #TODO quartermeister returns also slots 2+2 and 3+1 but with relative weight penalties
            slot_type = Slots.objects.get(quartermeister_required=True) 
        else:
            applicable_slots = Slots.objects.filter(quartermeister_required=False)
            weights = [slot.weight for slot in applicable_slots]
            slot_type = random.choices(applicable_slots, weights = weights, k = 1)[0]
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
        applicable_layouts = Layout.objects.filter(layout_type = slot)
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
        applicable_weapons = Weapon.objects.filter(weapon_type = weapon_type, size = size)
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

        primary_weapon = self.choose_weapon(layout_type.primary_type, slot_type.primary_size)
        secondary_weapon = self.choose_weapon(layout_type.secondary_type, slot_type.secondary_size)

        return primary_weapon, secondary_weapon

    




           
# class RandomCore():
#     """A сlass for holding special random methods
    
#     """

#     def __init__(self, weapons, chances):
#         self.guns = weapons
#         self.loadouts

#     #later it may import values of each layout probability
#     #now it's just a placeholder
#     #and it gets links
    

#     slots_3_2 = [ #all theese are 3+2 slot layouts, but they will have diffrent probability
#             ["rifle", "shotgun", 1], 
#             ["shotgun", "rifle", 0.9],             
#             ["shotgun", "shotgun", 0.7], 
#             ["rifle", "rifle", 0.7],
#             ["rifle", "pistol", 1],
#             ["shotgun", "pistol", 0.9],
#             ["misc", "rifle", 0.5],
#             ["misc", "shotgun", 0.5],
#             ["misc", "pistol", 0.5]
#     ]

#     slots_3_1 = [ #3+1 part but they will have diffrent probability
#             ["rifle", "pistol", 1],
#             ["shotgun", "misc", 0.6],
#             ["rifle", "misc", 0.8],
#             ["shotgun", "pistol", 0.8],
#             ["misc", "pistol", 0.5],
#     ]
#     slots_3_1_chance = 4

#     slots_2_2 = [ #2+2 part
#             ["rifle", "shotgun", 1],
#             ["shotgun", "shotgun", 0.5],
#             ["rifle", "rifle", 0.6],
#             ["pistol", "pistol", 0.3],
#     ]
#     slots_2_2_chance = 3

#     def get_loadout_style(self, quart):
#         """Function to decide what kind of slots a person will get.


#         This function uses weighted random distribution as its core.

#         Parameters
#         -----------
#         quart : bool
#             quartermeister decides whether you have 4 or 5 slots.
        
#         Returns
#         -----------
#         tuple of 2 elements
#             (1) : str - size of primary+secondary slot
#             (2) : list of 2 strings - types of slots to use
#         """
#         #potential feature - unique loadouts, like mosin avtomat + dual uppercuts
#         if quart:
#             slots = "3+2"
#             loadouts_types = [ x[:2] for x in self.slots_3_2] #take only first 2 values of each table
#             weights = [x[2] for x in self.slots_3_2] #extract only weight value
#         else:
#             slots = random.choices(("3+1", "2+2"), weights=[self.slots_3_1_chance,self.slots_2_2_chance])[0] #I try to balance 2 kinds of layouts so they appear equally
#             if slots == "3+1":
#                 loadouts_types = [ x[:2] for x in self.slots_3_1] 
#                 weights = [x[2] for x in self.slots_3_1]
#             else:
#                 loadouts_types = [ x[:2] for x in self.slots_2_2]
#                 weights = [x[2] for x in self.slots_2_2]
#         loadout = random.choices(loadouts_types, weights=weights, k=1)

#         return slots, loadout[0] #example

#     def get_a_gun(self, gun_type_class, size:int, debug = False) -> dict:
#         """
#         Gets a gun from a Weapon_type class, uses its .get_size_of() function.

#         Parameters
#         ---
#         gun_type_class : Weapon_type class
#             the class of gun to get
#         size : int
#             size of a gun 

#         Returns
#         ---
#         dict
#             all data of a weapon
#         (Debug returns only string - name)
#         """
#         gun_list = gun_type_class.get_size_of(size) #ask a weapon type class to give a list of applicable weapons
#         weights = [gun["Weight"] for gun in gun_list] #extract weight of each gun
#         the_gun = random.choices(gun_list, weights = weights, k = 1)[0] #choose a gun to use
#         #random.choices always returns a list, even of 1 item, so we unpack it with [0]
#         if debug:
#             return the_gun["Name"]
#         else:
#             return the_gun

#     def reroll(self, slot_to_reroll:str):
#         """rerolls only 1 single specified slot

#         Parameters
#         ---
#         slot_to_reroll : str
#             identifies which slot needs rerolling: "primary" or "secondary"

#         Returns
#         ---
#         dict
#             {"primary_gun": primary gun name, 
#             "primary_type": primary gun type
#             "primary_size": size of primary gun
#             "secondary_gun": secondary gun name,
#             "secondary_type": secondary gun type
#             "secondary_size": size of secondary gun 
#             "price": tuple of prices (primary, secondary)}

#         The same as from create_loadout() function, but an updated one.
#         """
#         try:
#             temporary_roll_storage = self.last_roll
#             if slot_to_reroll == "primary":
#                 size = temporary_roll_storage["primary_size"]
#                 slot_type = temporary_roll_storage["primary_type"]
#             else:
#                 size = temporary_roll_storage["secondary_size"]
#                 slot_type = temporary_roll_storage["secondary_type"]

#             new_roll = self.get_a_gun(self.gun_classes[slot_type], size)

#             if slot_to_reroll == "primary":
#                 self.last_roll["primary_gun"] = new_roll["Name"]
#                 self.last_roll["price"] = (new_roll["Price"], temporary_roll_storage["price"][1])
#             else:
#                 self.last_roll["secondary_gun"] = new_roll["Name"]
#                 self.last_roll["price"] = (temporary_roll_storage["price"][0], new_roll["Price"])

#         except AttributeError:
#             self.last_roll = {
#             "primary_gun": "Double dolch", 
#             "primary_type": "pistols",
#             "primary_size": 2,
#             "secondary_gun": "Double dolch",
#             "secondary_type": "pistols",
#             "secondary_size": 2, 
#             "price": (1500, 1500)
#             }
        
#         return self.last_roll
        


#     def create_loadout(self, quart:bool):
#         """Creates a loadout for your hunter.

#         Core function of the project. 

#         Parameters
#         ------------
#         quart : bool  
#             is quartermeister present
        
#         Returns
#         ------------
#         dict
#             {"primary_gun": primary gun name, 
#             "primary_type": primary gun type
#             "primary_size": size of primary gun
#             "secondary_gun": secondary gun name,
#             "secondary_type": secondary gun type
#             "secondary_size": size of secondary gun 
#             "Price": tuple of prices (primary, secondary)}
#         """
#         slots, [primary, secondary] = self.get_loadout_style(quart=quart)
#         if slots == "3+2":
#             primary_size = 3
#             secondary_size = 2
#         elif slots == "3+1":
#             primary_size = 3
#             secondary_size = 1
#         else: 
#             primary_size = 2
#             secondary_size = 2
#         primary_data = self.get_a_gun(self.gun_classes[primary], primary_size)
#         secondary_data = self.get_a_gun(self.gun_classes[secondary], secondary_size)

#         primary_gun, secondary_gun = primary_data["Name"], secondary_data["Name"]
#         summa = (primary_data["Price"], secondary_data["Price"])

#         self.last_roll = {
#             "primary_gun":primary_gun, 
#             "secondary_gun":secondary_gun, 
#             "price": summa, 
#             "primary_size": primary_size, 
#             "secondary_size": secondary_size,
#             "primary_type": primary,
#             "secondary_type": secondary
#             }

#         return self.last_roll

#     def wrap_a_roll(self, quart = False):
#         data = self.create_loadout(quart=quart)
#         return data["primary_gun"], data["secondary_gun"]

               
# shotguns = Weapon_Type("shotguns")
# rifles = Weapon_Type("rifles")
# pistols = Weapon_Type("pistols")
# misc = Weapon_Type("misc")
# major = RandomCore()


# if __name__ == "__main__":


#     # shotguns.print()

#     # print(rifles.get_size_of(3))
#     # print(rifles.arsenal)
#     # 
#     # print(major.get_a_gun(rifles,2))

#     # print(major.create_loadout(False))
#     print(major.wrap_a_roll(False))
#     # print(major.reroll("secondary"))



