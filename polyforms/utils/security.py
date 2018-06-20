import os

def get_secret_key(location):
    key = os.urandom(32)
    try:
        f = open(location, "r")
        key = f.read()
        f.close()
    except:
        f = open(location, "w")
        f.write(key)
        f.close()
    return key