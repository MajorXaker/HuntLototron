import hashlib


def encode_md5(*strings):
    """Connects any number of values into a single string, then MD5es it.
    Returns 32 char hex string. Truncate it if you need.
    """
    s_combined = "".join(strings)
    s_unspaced = [char for char in s_combined if char != " "]
    s_bytes = bytes("".join(s_unspaced), encoding="utf-8")
    code = hashlib.md5()
    code.update(s_bytes)
    encoded = code.hexdigest()
    return encoded
