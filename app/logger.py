import logging
import app

levels = ('INFO', 'DEBUG', 'WARNING', 'WARN', 'ERROR', 'FATAL', 'CRITICAL')

def configure():
    level = app.config['app', 'log']
    if level in levels:
        logging.basicConfig(level=getattr(logging, level))