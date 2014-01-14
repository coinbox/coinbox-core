import os

from .config import Config

def load(config_dir, data_dir, locale_dir):
    filename = os.path.join(config_dir, 'coinbox.json')
    return Config(filename)
