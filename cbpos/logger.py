from pydispatch import dispatcher

import os
import logging
logger = logging.getLogger(__name__)

import cbpos

cbpos.config.set_default('app', 'log', 'INFO')
cbpos.config.set_default('app', 'log_file', '')

levels = ('INFO', 'DEBUG', 'WARNING', 'WARN', 'ERROR', 'FATAL', 'CRITICAL')

def configure():
    level = cbpos.config['app', 'log']
    level = getattr(logging, level if level in levels else levels[0])
    
    filename = cbpos.config['app', 'log_file']
    filepath = os.path.realpath(filename) if filename != '' else None
    
    if filepath is None:
        logging.basicConfig(level=level)
    else:
        logging.basicConfig(level=level, filename=filepath)
    
    dispatcher.connect(log_signals, signal=dispatcher.Any, sender=dispatcher.Any)

def log_signals(sender, signal, *args, **kwargs):
    logger.debug('Signal %s received from %s: %s, %s' % (signal, sender, args, kwargs))