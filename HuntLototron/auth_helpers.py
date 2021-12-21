class AuthShowdown():

    def credentials_to_dict(url_request, debug=False):
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
        }

        if debug:
            print (user)

        return user