__all__ = ('run', 'terminate', 'use_translation', 'load_database', 'break_init', 'set_main_window', 'load_menu', 'start', 'res_path')

import sys, os, argparse
import PySide
from PySide import QtGui

import logging
logger = logging.getLogger(__name__)

import app

app.config.set_default('app', 'fullscreen', '')
app.config.set_default('app', 'first_run', '1')
app.config.set_default('app', 'log', '1')

logger.info('Python: %s' % (sys.version,))
logger.info('Platform: %s' % (sys.platform,))
logger.info('PySide: %s' % (PySide.__version_info__,))

logger.debug('Creating menu...')
import app.menu
app.menu.init()

logger.debug('Importing database...')
import app.database

logger.debug('Importing modules...')
import app.modules
app.modules.init()

def parse_args():
    # TODO: Careful!! We are using another version of argparse that does not ship with Python2.7
    # (I think it does with Python3.1) So there is a file called argparse.py
    # You will not be able to run the app without it.
    logger.debug('Parsing arguments. argparse is version ' + argparse.__version__)
    
    app.parser = argparse.ArgumentParser(description=app.description)
    
    app.subparsers = app.parser.add_subparsers(dest='subparser_name')
    
    # Load module-specific command-line arguments
    app.modules.parse_args()
    
    app.args = app.parser.parse_args()
    
    if hasattr(app.args, "handle"):
        app.args.handle(app.args)

def init_translation(use=True):
    if not use:
        tr_builder = app.DummyTranslatorBuilder()
        
        logger.info("Translation disabled.")
    else:
        localedir = app.config['locale', 'localedir']
        languages = app.config['locale', 'languages']
        fallback = app.config['locale', 'fallback'] == '1'
        codeset = app.config['locale', 'codeset']
        class_ = None # No need for a custom GNUTranslation class
        
        logger.debug("Using [%s](codeset:%s) for translation with fallback=%s in %s" % (languages, codeset, fallback, localedir))
        
        tr_builder = app.TranslatorBuilder(localedir=os.path.abspath(localedir),
                                           languages=None if languages == "" else languages.split(","),
                                           class_=class_,
                                           fallback=fallback,
                                           codeset=codeset)
    
    app.modules.init_translators(tr_builder)
    tr_builder.install()

def start():
    global _main_window
    logger.debug('Importing main window...')
    from app.window import MainWindow
    
    app.config['app', 'first_run'] = ''
    _main_window = MainWindow()
    
    logger.debug('Loading menu...')
    _main_window.loadMenu()
    
    fullscreen = (app.config['app', 'fullscreen'] != '')
    if fullscreen:
        _main_window.showFullScreen()
    else:
        _main_window.show()

def terminate():
    try:
        logger.info('Terminating application...')
    except:
        pass

def run():
    """
    Main function to run the application.
    """
    global _main_window, _load_database, _break_init
    logger.debug('Running application...')
    
    if app.config['app', 'first_run'] or app.config.empty():
        # Force configuration if configuration is empty.
        app.config.save_defaults(overwrite=False)
        logger.info('First run. Saving configuration...')
    
    logger.debug('Creating application instance...')
    app.main = QtGui.QApplication(sys.argv)
    
    parse_args()
    
    locale_use = (app.config['locale', 'use'] == '1')
    init_translation(use=(_use_translation and locale_use))
    
    if _load_database:
        if not app.database.init():
            return
        # Load database objects of every module
        app.modules.load_database()
    else:
        logger.debug('Did not load database.')
    
    if _load_menu:
        logger.debug('Extending menu...')
        # Load appropriate menu items from all the modules
        app.modules.extend_menu(app.menu.main)
        app.menu.main.sort()
    else:
        logger.debug('Did not load menu.')
    
    if _break_init:
        logger.debug('Break init.')
    else:
        logger.debug('Initializing modules...')
        # Initiate every installed module
        for mod in app.modules.all():
            init = mod.init()
            if not init:
                logger.fatal('Initializing module %s failed.' % (mod.base_name,))
                return False
            elif _break_init:
                break
    
    if _main_window is None:
        start()
    else:
        logger.debug('Main Window is not the default: ' + repr(_main_window))
        _main_window.show()
    return app.main.exec_()

_use_translation = True
_load_database = True
_load_menu = True
_break_init = False
_main_window = None

def use_translation(on=True):
    global _use_translation
    _use_translation = on

def load_database(on=True):
    global _load_database
    _load_database = on

def load_menu(on=True):
    global _load_menu
    _load_menu = on

def set_main_window(win=None):
    global _main_window
    _main_window = win

def break_init(on=True):
    global _break_init
    _break_init = on
    
def res_path():
    return './res'