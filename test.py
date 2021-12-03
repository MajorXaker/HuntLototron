k = [{'Name': 'Crown', 'Player_name': 'Корона', 'Core_gun': 'Crown & King Auto-5', 'Sights': 'Iron', 'Melee': 'None', 'Size': 'Full', 'Size_num': '3', 'Weight': '1', 'Price': '600'},
{'Name': 'Specter 1882', 'Player_name': 'Спектр', 'Core_gun': 'Specter 1882', 'Sights': 'Iron', 'Melee': 'None', 'Size': 'Full', 'Size_num': '3', 'Weight': '1', 'Price': '188'},
{'Name': 'Specter 1883 Bayonet', 'Player_name': 'Спектр штык', 'Core_gun': 'Specter 1883', 'Sights': 'Iron', 'Melee': 'Bayonet', 'Size': 'Full', 'Size_num': '3', 'Weight': '1', 'Price': '223'},
{'Name': 'Specter 1882 Compact', 'Player_name': 'Спектр обрез', 'Core_gun': 'Specter 1884', 'Sights': 'Iron', 'Melee': 'None', 'Size': 'Compact', 'Size_num': '2', 'Weight': '1', 'Price': '164'}]

# print(k)

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
# a = [ x[:2] for x in slots_3_2]
# b = [x[2] for x in slots_3_2]

# a = [1,2,3,4]
# b = [4,6,7,8]
# print(a+b)

# a = [x["Weight"] for x in k]
# print(a)

dictionary = {"primary_gun": "primary", "secondary_gun": "secondary", "Price": "summa"}

# a, b, c = dictionary["primary_gun", "secondary_gun", "Price"]
# a, b, c = data["primary_gun"], data["secondary_gun"], data["Price"]

# try:
#     print(qq)
# except NameError:
#     print("No qq")

# a = "primary"
# 
# print(dictionary[a+"_gun"])


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

multikey = "primary_gun", "secondary_gun", "Price"

a = multiget(dictionary, multikey)

a = "alphabet"
print(a["a"])
