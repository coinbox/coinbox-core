from pydispatch import dispatcher

import logging
logger = logging.getLogger(__name__)

import cbpos

levels = ('INFO', 'DEBUG', 'WARNING', 'WARN', 'ERROR', 'FATAL', 'CRITICAL')

def configure():
    level = cbpos.config['app', 'log']
    if level in levels:
        logging.basicConfig(level=getattr(logging, level))
    
    dispatcher.connect(log_signals, signal=dispatcher.Any, sender=dispatcher.Any)

def log_signals(sender, signal, *args, **kwargs):
    logger.debug('Signal %s received from %s: %s, %s' % (signal, sender, args, kwargs))