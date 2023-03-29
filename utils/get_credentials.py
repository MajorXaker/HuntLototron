from django.contrib.auth.models import User, AnonymousUser
from django.core.handlers.wsgi import WSGIRequest
from pydantic import BaseModel

from stats.models import Player


class UserCredsOrganised(BaseModel):
    anonymous: bool
    has_aka: bool
    username: str
    playername: str | None
    credentials: tuple[str, str | None]
    name: str
    user: User | AnonymousUser
    player: Player | None
    position: int = None

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_request(cls, url_request: WSGIRequest):
        username = url_request.user.username
        player = getattr(url_request.user, "username_of_player", None)
        playername = getattr(player, "also_known_as", None)

        organised_creds = cls(
            anonymous=username == "",
            has_aka=bool(playername),
            username=username,
            playername=playername,
            credentials=(username, playername),
            name=playername or username,
            user=url_request.user,
            player=player,
        )
        return organised_creds

    def set_position(self, pos):
        self.position = pos


def get_credentials(url_request: WSGIRequest, debug=False):
    """Exports usable data on current logged user
    DEPRECATED

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
