import csv

"""
[id,wl_status,date,kills_total,playtime,bounty,map,
player_1,player_1_primary_weapon,player_1_primary_ammo_A,player_1_primary_ammo_B,player_1_secondary_weapon,player_1_secondary_ammo_A,
player_1_secondary_ammo_B,player_1_kills,player_1_assists,player_1_deaths,player_1_signature,
player_2,player_2_primary_weapon,player_2_primary_ammo_A,player_2_primary_ammo_B,player_2_secondary_weapon,player_2_secondary_ammo_A,
player_2_secondary_ammo_B,player_2_kills,player_2_assists,player_2_deaths,player_2_signature,
player_3,player_3_primary_weapon,player_3_primary_ammo_A,player_3_primary_ammo_B,player_3_secondary_weapon,player_3_secondary_ammo_A,
player_3_secondary_ammo_B,player_3_kills,player_3_assists,player_3_deaths,player_3_signature,correct_match,fights_locations
]"""

class CozyList():
    class CozyItem():
        def __init__(self, name, rank) -> None:
            self.name = name
            self.rank = rank
    
    def __init__(self) -> None:
        self.data = []
    
    def __getitem__(self, item):
        return self.data[item]

    def append(self, name, rank):
        item = self.CozyItem(name, rank)
        self.data.append(item)
    
    def print(self):
        for line in self.data:
            print(line.name + " - " + line.rank)


my_list = CozyList()
my_list.append("Jack O'Neill", 'Brigade General')
my_list.append("Cameron Mitchell", 'Leutenant Colonel')
my_list.append("Samantha Carter", 'Leutenant Colonel')
my_list.append("Teal'c", 'Jaffa')
my_list.append("Daniel Jackson", 'Non-Military personnel')

print(my_list[3].name)