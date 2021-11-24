import csv
import random

# #as always, something in my system changes the current dir to F:/Git
# from pathlib import Path
# import os
# #load important stuff
# path_to_script = os.path.realpath(__file__) #get path to file location
# current_path = Path(path_to_script) #remove the name of the file
# os.chdir(current_path.parent) #change directory to match the current location


class Weapon_Type():
    """
    Class for storing and accessing a class of weapons

    """
    

    def __init__(self, filename):
        self.arsenal = {}
        filename = filename + ".csv"
        with open(filename) as csv_file:
            csv.register_dialect("hunt", delimiter = ";") #state that delimeter here not , but ;
            #read csv as dictionary with stated field names and dialect
            csv_data = csv.DictReader(csv_file, fieldnames=["Name", "Player_name", "Core_gun", "Sights", "Melee", "Size", "Size_num", "Weight", "Price"], dialect = "hunt")
            rowID = 0
            for row in csv_data:
                if rowID == 0:
                    rowID += 1
                else:
                    #in csv file all values are strings, conver them for convenience
                    row["Size_num"] = int(row["Size_num"])
                    row["Price"] = int(row["Price"])
                    try: #in case some bugs - return weight to default
                        row["Weight"] = float(row["Weight"])
                    except TypeError:
                        row["Weight"] = 1
                    
                    self.arsenal[row["Name"]] = row
            csv_data = None
                    
    def print(self):
        """Method for debug purposes

        Show a class content in a neat way; no arguments, just prints it out.
        """ 
        for key in self.arsenal:
            print(self.arsenal[key])

    
    def get_size_of(self, size, debug = False) -> list: 
        """Method for getting a list for randomization function, gets guns of needed size.


        Parameters
        -----------
        Size : int
            1 to 3, size in slots.
        dedug : bool
            wheter to return a list of names instead of complete list

        Returns
        ----------
        list
            A list of guns which fall into the criteria of size

        """
        applicable = [gun for gun in list(self.arsenal.values()) if gun["Size_num"] == size]

        if debug:
            return [x["Name"] for x in applicable]
        else:
            return applicable

            
class RandomCore():
    """A сlass for holding special random methods


    
    """

    def __init__(self):
        self.rifles = rifles
        self.shotguns = shotguns
        self.pistols = pistols
        self.misc = misc
    
        self.gun_classes = {
            "rifle" : self.rifles, 
            "shotgun" : self.shotguns, 
            "pistol" : self.pistols, 
            "misc" : self.misc 
            }

    #later it may import values of each layout probability
    #now it's just a placeholder
    #and it gets links
    

    slots_3_2 = [ #all theese are 3+2 slot layouts, but they will have diffrent probability
            ["rifle", "shotgun", 1], 
            ["shotgun", "rifle", 0.9],             
            ["shotgun", "shotgun", 0.7], 
            ["rifle", "rifle", 0.7],
            ["rifle", "pistol", 1],
            ["shotgun", "pistol", 0.9],
            ["misc", "rifle", 0.5],
            ["misc", "shotgun", 0.5],
            ["misc", "pistol", 0.5]
    ]

    slots_3_1 = [ #3+1 part but they will have diffrent probability
            ["rifle", "pistol", 1],
            ["shotgun", "misc", 0.6],
            ["rifle", "misc", 0.8],
            ["shotgun", "pistol", 0.8],
            ["misc", "pistol", 0.5],
    ]
    slots_3_1_chance = 4

    slots_2_2 = [ #2+2 part
            ["rifle", "shotgun", 1],
            ["shotgun", "shotgun", 0.5],
            ["rifle", "rifle", 0.6],
            ["pistol", "pistol", 0.3],
    ]
    slots_2_2_chance = 3

    def get_loadout_style(self, quart):
        """Function to decide what kind of slots a person will get.


        This function uses weighted random distribution as its core.

        Parameters
        -----------
        quart : bool
            quartermeister decides whether you have 4 or 5 slots.
        
        Returns
        -----------
        tuple of 2 elements
            (1) : str - size of primary+secondary slot
            (2) : list of 2 strings - types of slots to use
        """
        #potential feature - unique loadouts, like mosin avtomat + dual uppercuts
        if quart:
            slots = "3+2"
            loadouts_types = [ x[:2] for x in self.slots_3_2] #take only first 2 values of each table
            weights = [x[2] for x in self.slots_3_2] #extract only weight value
        else:
            slots = random.choices(("3+1", "2+2"), weights=[self.slots_3_1_chance,self.slots_2_2_chance])[0] #I try to balance 2 kinds of layouts so they appear equally
            if slots == "3+1":
                loadouts_types = [ x[:2] for x in self.slots_3_1] 
                weights = [x[2] for x in self.slots_3_1]
            else:
                loadouts_types = [ x[:2] for x in self.slots_2_2]
                weights = [x[2] for x in self.slots_2_2]
        loadout = random.choices(loadouts_types, weights=weights, k=1)

        return slots, loadout[0] #example

    def get_a_gun(self, gun_type_class, size:int, debug = False) -> dict:
        """
        Gets a gun from a Weapon_type class, uses its .get_size_of() function.

        Parameters
        ---
        gun_type_class : Weapon_type class
            the class of gun to get
        size : int
            size of a gun 

        Returns
        ---
        dict
            all data of a weapon
        (Debug returns only string - name)
        """
        gun_list = gun_type_class.get_size_of(size) #ask a weapon type class to give a list of applicable weapons
        weights = [gun["Weight"] for gun in gun_list] #extract weight of each gun
        the_gun = random.choices(gun_list, weights = weights, k = 1)[0] #choose a gun to use
        #random.choices always returns a list, even of 1 item, so we unpack it with [0]
        if debug:
            return the_gun["Name"]
        else:
            return the_gun

    def reroll(self, slot_to_reroll:str):
        """rerolls only 1 single specified slot

        Parameters
        ---
        slot_to_reroll : str
            identifies which slot needs rerolling: "primary" or "secondary"

        Returns
        ---
        dict
            {"primary_gun": primary gun name, 
            "primary_type": primary gun type
            "primary_size": size of primary gun
            "secondary_gun": secondary gun name,
            "secondary_type": secondary gun type
            "secondary_size": size of secondary gun 
            "price": tuple of prices (primary, secondary)}

        The same as from create_loadout() function, but an updated one.
        """
        try:
            temporary_roll_storage = self.last_roll
            if slot_to_reroll == "primary":
                size = temporary_roll_storage["primary_size"]
                slot_type = temporary_roll_storage["primary_type"]
            else:
                size = temporary_roll_storage["secondary_size"]
                slot_type = temporary_roll_storage["secondary_type"]

            new_roll = self.get_a_gun(self.gun_classes[slot_type], size)

            if slot_to_reroll == "primary":
                self.last_roll["primary_gun"] = new_roll["Name"]
                self.last_roll["price"] = (new_roll["Price"], temporary_roll_storage["price"][1])
            else:
                self.last_roll["secondary_gun"] = new_roll["Name"]
                self.last_roll["price"] = (temporary_roll_storage["price"][0], new_roll["Price"])

        except AttributeError:
            self.last_roll = {
            "primary_gun": "Double dolch", 
            "primary_type": "pistols",
            "primary_size": 2,
            "secondary_gun": "Double dolch",
            "secondary_type": "pistols",
            "secondary_size": 2, 
            "price": (1500, 1500)
            }
        
        return self.last_roll
        


    def create_loadout(self, quart:bool):
        """Creates a loadout for your hunter.

        Core function of the project. 

        Parameters
        ------------
        quart : bool  
            is quartermeister present
        
        Returns
        ------------
        dict
            {"primary_gun": primary gun name, 
            "primary_type": primary gun type
            "primary_size": size of primary gun
            "secondary_gun": secondary gun name,
            "secondary_type": secondary gun type
            "secondary_size": size of secondary gun 
            "Price": tuple of prices (primary, secondary)}
        """
        slots, [primary, secondary] = self.get_loadout_style(quart=quart)
        if slots == "3+2":
            primary_size = 3
            secondary_size = 2
        elif slots == "3+1":
            primary_size = 3
            secondary_size = 1
        else: 
            primary_size = 2
            secondary_size = 2
        primary_data = self.get_a_gun(self.gun_classes[primary], primary_size)
        secondary_data = self.get_a_gun(self.gun_classes[secondary], secondary_size)

        primary_gun, secondary_gun = primary_data["Name"], secondary_data["Name"]
        summa = (primary_data["Price"], secondary_data["Price"])

        self.last_roll = {
            "primary_gun":primary_gun, 
            "secondary_gun":secondary_gun, 
            "price": summa, 
            "primary_size": primary_size, 
            "secondary_size": secondary_size,
            "primary_type": primary,
            "secondary_type": secondary
            }

        return self.last_roll

    def wrap_a_roll(self, quart = False):
        data = self.create_loadout(quart=quart)
        return data["primary_gun"], data["secondary_gun"]

               
shotguns = Weapon_Type("shotguns")
rifles = Weapon_Type("rifles")
pistols = Weapon_Type("pistols")
misc = Weapon_Type("misc")
major = RandomCore()


if __name__ == "__main__":


    # shotguns.print()

    # print(rifles.get_size_of(3))
    # print(rifles.arsenal)
    # 
    # print(major.get_a_gun(rifles,2))

    # print(major.create_loadout(False))
    print(major.wrap_a_roll(False))
    # print(major.reroll("secondary"))



