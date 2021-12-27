import hashlib
from typing_extensions import Required

class AuxClass():

    def credentials_to_dict(url_request, debug=False):
        '''Exports usable data on current logged user

        'anonymous': is_anon,
        'has_aka': has_aka,
        'username': username,
        'playername': playername,
        'credentials': (username, playername),
        'name' : aka or username
        'user' : userclass of active user
        '''
        username = url_request.user.username
        user = {
        'username': username,
        }

        try:
            playername = url_request.user.username_of_player.also_known_as
            has_aka = True if playername != '' else False
            
        except AttributeError:
            playername = None
            has_aka = False
            

        name = playername if has_aka else username
        

        is_anon = True if username == '' else False

        user = {
            'anonymous': is_anon,
            'has_aka': has_aka,
            'username': username,
            'playername': playername,
            'credentials': (username, playername),
            'name' : name,
            'user':url_request.user,
        }

        if debug:
            print (user)

        return user

    def encode_md5(*strings):
        '''Connects any number of values into a single string, then MD5es it.
        Returns 32 char hex string. Truncate it if you need.
        '''
        s_combined = ''.join(strings)
        s_unspaced = [char for char in s_combined if char != ' ']
        s_bytes = bytes(''.join(s_unspaced), encoding='utf-8')
        code = hashlib.md5()
        code.update(s_bytes)
        encoded = code.hexdigest()
        return encoded

        


