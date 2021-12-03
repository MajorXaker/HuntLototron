import csv


typecode = {"Rifle":1, "Pistol":2, "Shotgun":3, "Misc":4}

with open("misc.csv", ) as csv_file:
    csv.register_dialect("hunt", delimiter = ";")
    field_names = ["Name", "Player_name", "Core_gun", "Sights", "Muzzle", "Melee", "Size_num", "Weight", "Price"]
    csv_data = csv.DictReader(csv_file, fieldnames=field_names, dialect = "hunt")
    arsenal = []
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
            row["Gun_type"] = typecode["Misc"]
            
            arsenal.append(row)

# print(arsenal[0])

import sqlite3
import json

def multiget(iterable, keys, default_value = 0):
    """Function for getting a lot of values at ones by their keys

    This function raises TypeError if you try to access iterable with strings instead of numerical keys. Strings are only for dicts!
    Parameters
    ---
    iterable 
        any iterable object with get method - will use get(key)
        or other iterable - tries to work positionally iterable[key]
    keys
        iterable with keys to access
    default_value 
        a value to give when needed value does not exist
        
    Returns
    -----
        list of values accessed in order of keys given    
    """
    output = []
    if isinstance(iterable, dict) or isinstance(iterable, list):
        for key in keys:
            output.append(iterable.get(key, default_value))
    else:
        output.append(iterable[key])
    return output

keys = (
    "Name",
    "Core_gun",
    "Size_num",
    "Weight",
    "Price",
    "Gun_type",
    "Sights",
    "Muzzle",
    "Melee"
    )

with sqlite3.connect("HuntLototron\db.sqlite3") as conn:
    command = "INSERT INTO roulette_weapon (name, core_gun, size, weight, price, gun_type_id, sights, muzzle, melee ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)" #this command uses sql language
  
    for gun in arsenal:
        data_to_sql = multiget(gun, keys)
        conn.execute(command, tuple(data_to_sql)) #we don't past raw key-value pairs, we need just values
    conn.commit() #needed only for writing