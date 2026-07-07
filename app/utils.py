import string
import random

CHARS = string.ascii_letters + string.digits   # a-z A-Z 0-9 = 62 characters
DEFAULT_LENGTH = 7


def generate_short_code(length: int = DEFAULT_LENGTH) -> str:
    """
    Generates a random alphanumeric string.
    62^7 = ~3.5 trillion possible codes — collisions are astronomically rare
    but the calling code must still handle them.
    """
    return "".join(random.choices(CHARS, k=length))
