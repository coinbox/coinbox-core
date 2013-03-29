from pydispatch import dispatcher

import os, logging

import cbpos

cbpos.config.set_default('app', 'log', 'INFO')
cbpos.config.set_default('app', 'log_file', '')
cbpos.config.set_default('app', 'log_use_colors', '')

LEVELS = ('INFO', 'DEBUG', 'WARNING', 'WARN', 'ERROR', 'FATAL', 'CRITICAL')

def get_logger(name):
    """
    Proxy to the logging.getLogger method.
    """
    return logging.getLogger(name)

logger = get_logger(__name__)

def configure():
    level = cbpos.config['app', 'log']
    level = getattr(logging, level if level in LEVELS else LEVELS[0])
    
    filename = cbpos.config['app', 'log_file']
    filepath = os.path.realpath(filename) if filename != '' else None
    
    use_colors = bool(cbpos.config['app', 'log_use_colors'])
    
    root = logging.getLogger() 
    root.setLevel(level)
    
    # The standard format used for file logging and console logging
    log_format = '%(name)s: %(message)s (%(filename)s:%(lineno)s)'
    long_log_format = '[%(levelname)s]\t'+log_format
    
    console = logging.StreamHandler()
    
    # Format with colors
    if use_colors and ColoredFormatter is not None:
        console.setFormatter(ColoredFormatter(log_format))
    else:
        console.setFormatter(logging.Formatter(long_log_format))
    root.addHandler(console)
    
    if filepath:
        # Set up logging to a file
        fh = logging.FileHandler(filepath, 'w')
        fh.setFormatter(logging.Formatter(long_log_format))
        root.addHandler(fh)
    
    # Log any signal from any sender
    dispatcher.connect(log_signals, signal=dispatcher.Any, sender=dispatcher.Any)

def log_signals(sender, signal, *args, **kwargs):
    """
    Log all signals sent from PyDispatcher.
    """
    logger.debug('Signal %s received from %s: %s, %s' % (signal, sender, args, kwargs))

try:
    # Try to import clint for colored logging
    from clint.textui import colored
    import copy
except ImportError:
    ColoredFormatter = None
except:
    raise
else:
    class ColoredFormatter(logging.Formatter):
        """
        Logging formatter which processes the logging messages in a clear, colorful way.
        Requires clint to work.
        """
        LEVELCOLOR = {
            'DEBUG': 'white',
            'INFO': 'green',
            'WARNING': 'magenta',
            'WARN': 'magenta',
            'ERROR': 'red',
            'CRITICAL': 'yellow',
            }
        NAMECOLOR = 'blue'
        FILECOLOR = 'green'
        
        lastname = ''
    
        def colorstr(self, string, color):
            if colored is None:
                return string
            return getattr(colored, color)(string)
    
        def format(self, record):
            record = copy.copy(record)
            levelname = record.levelname
            
            if record.name == self.lastname:
                record.name = ' '*len(record.name)
            else:
                self.lastname = record.name
            
            if levelname in self.LEVELCOLOR:
                record.levelname = self.colorstr(levelname, self.LEVELCOLOR[levelname])
                record.name = self.colorstr(record.name, self.NAMECOLOR)
                record.msg = self.colorstr(record.msg, self.LEVELCOLOR[levelname])
                record.filename = self.colorstr(record.filename, self.FILECOLOR)
                record.lineno = self.colorstr(record.lineno, self.FILECOLOR)
            return logging.Formatter.format(self, record)
