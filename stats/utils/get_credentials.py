from django.core.handlers.wsgi import WSGIRequest


def get_credentials(url_request: WSGIRequest, debug=False):
    """Exports usable data on current logged user

    'anonymous': is_anon,
    'has_aka': has_aka,
    'username': username,
    'playername': playername,
    'credentials': (username, playername),
    'name' : aka or username
    'user' : userclass of active user
    """
    username = url_request.user.username
    # TODO remove try\except
    try:
        playername = url_request.user.username_of_player.also_known_as
        has_aka = True if playername != "" else False

    except AttributeError:
        playername = None
        has_aka = False

    name = playername if has_aka else username

    is_anon = True if username == "" else False

    user = {
        "anonymous": is_anon,
        "has_aka": has_aka,
        "username": username,
        "playername": playername,
        "credentials": (username, playername),
        "name": name,
        "user": url_request.user,
    }

    if debug:
        print(user)

    return user
