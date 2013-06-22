from .config import Config

def load():
    filename = 'coinbox.json'
    return Config(filename)
