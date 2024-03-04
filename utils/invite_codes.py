import string
from random import choice


def create_code(size: int = 8):
    valid_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return "".join(choice(valid_chars) for _ in range(size))
